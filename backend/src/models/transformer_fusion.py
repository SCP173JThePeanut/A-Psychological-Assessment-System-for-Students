# src/models/transformer_fusion.py
"""
Transformer融合模型定义 - 修正导入问题
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Tuple
import sys
import os
import numpy as np
# 添加父目录到路径，以便导入base_model
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from .base_model import BaseMentalHealthModel

    print("✓ 使用相对导入")
except ImportError:
    try:
        from src.models.base_model import BaseMentalHealthModel

        print("✓ 使用绝对导入")
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        # 如果都失败，定义基类（临时方案）
        print("⚠ 使用临时基类定义")


        class BaseMentalHealthModel(nn.Module):
            """临时基类"""

            def __init__(self, face_dim=13, audio_dim=21, hr_dim=9, num_classes=4, device="cpu"):
                super().__init__()
                self.face_dim = face_dim
                self.audio_dim = audio_dim
                self.hr_dim = hr_dim
                self.num_classes = num_classes
                self.device = device
                self.class_names = ["正常", "轻度压力", "中度压力", "重度压力"]
                self.is_trained = False


class TransformerFusionModel(BaseMentalHealthModel):
    """基于Transformer的多模态融合模型"""

    def __init__(self,
                 face_dim: int = 13,
                 audio_dim: int = 21,
                 hr_dim: int = 9,
                 num_classes: int = 4,
                 hidden_dim: int = 64,
                 num_heads: int = 4,
                 num_layers: int = 2,
                 dropout: float = 0.1,
                 device: str = "cpu"):
        """
        初始化Transformer融合模型
        """
        super().__init__(face_dim, audio_dim, hr_dim, num_classes, device)

        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.dropout = dropout

        # 更新配置
        self.config = {
            "face_dim": face_dim,
            "audio_dim": audio_dim,
            "hr_dim": hr_dim,
            "num_classes": num_classes,
            "hidden_dim": hidden_dim,
            "num_heads": num_heads,
            "num_layers": num_layers,
            "dropout": dropout
        }

        # 1. 特征投影层
        self.face_projection = nn.Sequential(
            nn.Linear(face_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        self.audio_projection = nn.Sequential(
            nn.Linear(audio_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        self.hr_projection = nn.Sequential(
            nn.Linear(hr_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout)
        )

        # 2. 模态编码
        self.modal_embeddings = nn.Embedding(3, hidden_dim)

        # 3. Transformer编码器
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim * 4,
            dropout=dropout,
            batch_first=True,
            device=device
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers
        )

        # 4. 模态贡献度计算层
        self.contribution_network = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1)
        )

        # 5. 分类头
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim * 2),
            nn.BatchNorm1d(hidden_dim * 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_classes)
        )

        # 将模型移到指定设备
        self.to(device)

    def forward(self,
                face_features: torch.Tensor,
                audio_features: torch.Tensor,
                hr_features: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        前向传播
        """
        batch_size = face_features.shape[0]

        # 1. 特征投影
        face_emb = self.face_projection(face_features)  # [batch, hidden]
        audio_emb = self.audio_projection(audio_features)  # [batch, hidden]
        hr_emb = self.hr_projection(hr_features)  # [batch, hidden]

        # 2. 添加模态编码
        modal_ids = torch.arange(3, device=self.device).unsqueeze(0).expand(batch_size, -1)  # [batch, 3]
        modal_emb = self.modal_embeddings(modal_ids)  # [batch, 3, hidden]

        # 3. 准备Transformer输入
        features = torch.stack([face_emb, audio_emb, hr_emb], dim=1)  # [batch, 3, hidden]
        features = features + modal_emb

        # 4. Transformer编码
        encoded_features = self.transformer_encoder(features)  # [batch, 3, hidden]

        # 5. 计算模态贡献度
        # 重塑encoded_features为 [batch*3, hidden_dim]
        batch_size, num_modals, hidden_dim = encoded_features.shape
        flat_features = encoded_features.reshape(-1, hidden_dim)  # [batch*3, hidden]

        # 通过贡献度网络得到每个模态的分数
        flat_scores = self.contribution_network(flat_features)  # [batch*3, 1]

        # 重塑回 [batch, 3]
        contribution_scores = flat_scores.reshape(batch_size, num_modals)  # [batch, 3]

        # 使用softmax得到归一化的贡献度
        modal_contributions = F.softmax(contribution_scores, dim=-1)  # [batch, 3]

        # 6. 加权融合
        weighted_features = (encoded_features * modal_contributions.unsqueeze(-1)).sum(dim=1)  # [batch, hidden]

        # 7. 分类
        all_features = encoded_features.reshape(batch_size, -1)  # [batch, 3*hidden]
        predictions = self.classifier(all_features)

        # 8. 返回结果
        contributions = {
            "modal_contributions": modal_contributions,
            "encoded_features": encoded_features,
            "contribution_scores": contribution_scores
        }

        return predictions, contributions

    def get_feature_contributions(self,
                                  face_features: torch.Tensor,
                                  audio_features: torch.Tensor,
                                  hr_features: torch.Tensor) -> Dict[str, float]:
        """
        获取各模态特征贡献度 - 修正版

        返回:
            Dict[str, float]: 各模态贡献度百分比 (0-100%)
        """
        # 前向传播获取贡献度
        _, contributions = self(face_features, audio_features, hr_features)
        modal_contributions = contributions["modal_contributions"]  # [batch, 3]

        # 计算平均贡献度
        avg_contributions = modal_contributions.mean(dim=0)  # [3]

        # 确保是百分比 (0-100)
        total = avg_contributions.sum().item()
        if abs(total - 1.0) > 0.01:  # 如果不是1，重新归一化
            avg_contributions = avg_contributions / total

        # 转换为百分比字典
        return {
            "face": avg_contributions[0].item() * 100,
            "audio": avg_contributions[1].item() * 100,
            "hr": avg_contributions[2].item() * 100
        }

    def predict(self,
                face_features: np.ndarray,
                audio_features: np.ndarray,
                hr_features: np.ndarray,
                return_contributions: bool = True) -> Dict[str, any]:
        """
        预测心理健康状态
        """
        import numpy as np

        # 转换为torch tensor
        face_tensor = torch.FloatTensor(face_features).to(self.device)
        audio_tensor = torch.FloatTensor(audio_features).to(self.device)
        hr_tensor = torch.FloatTensor(hr_features).to(self.device)

        if len(face_tensor.shape) == 1:
            face_tensor = face_tensor.unsqueeze(0)
        if len(audio_tensor.shape) == 1:
            audio_tensor = audio_tensor.unsqueeze(0)
        if len(hr_tensor.shape) == 1:
            hr_tensor = hr_tensor.unsqueeze(0)

        # 设置模型为评估模式
        self.eval()

        with torch.no_grad():
            # 前向传播
            predictions, _ = self(face_tensor, audio_tensor, hr_tensor)

            # 获取预测类别和概率
            probs = torch.softmax(predictions, dim=-1)
            pred_class = torch.argmax(probs, dim=-1)
            confidence = torch.max(probs, dim=-1).values
            score = self.compute_score(probs)  # 新增：计算分数

            # 获取贡献度
            if return_contributions:
                modal_contributions = self.get_feature_contributions(
                    face_tensor, audio_tensor, hr_tensor
                )
            else:
                modal_contributions = {}

        # 转换为numpy
        pred_class_np = pred_class.cpu().numpy()
        confidence_np = confidence.cpu().numpy()
        probs_np = probs.cpu().numpy()

        # 构建结果字典
        results = {
            "predictions": pred_class_np,
            "confidence": confidence_np,
            "probabilities": probs_np,
            "score": score.cpu().numpy(),  # 添加分数
            "class_names": [self.class_names[c] for c in pred_class_np]
        }

        if return_contributions:
            results["contributions"] = modal_contributions

            # 生成解释文本
            results["explanation"] = self._generate_explanation(
                pred_class_np[0],
                confidence_np[0],
                modal_contributions
            )

        return results

    def _generate_explanation(self, pred_class, confidence, contributions, score):
        class_name = self.class_names[pred_class]
        sorted_contrib = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
        explanation_parts = [
            f"心理压力分数: {score:.1f}，属于{class_name}状态，置信度{confidence:.1%}",
            "主要依据："
        ]
        for modality, contrib in sorted_contrib:
            if contrib > 0.1:
                modality_name = {"face": "面部表情", "audio": "语音特征", "hr": "心率信号"}.get(modality, modality)

                explanation_parts.append(f"- {modality_name}贡献{(contrib*0.01):.2%}")

        return "\n".join(explanation_parts)

    def summary(self):
        """打印模型摘要"""
        print("=" * 60)
        print(f"模型: {self.__class__.__name__}")
        print(f"设备: {self.device}")
        print(f"输入维度:")
        print(f"  面部特征: {self.face_dim}")
        print(f"  语音特征: {self.audio_dim}")
        print(f"  心率特征: {self.hr_dim}")
        print(f"  总维度: {self.face_dim + self.audio_dim + self.hr_dim}")
        print(f"输出类别: {self.num_classes} ({', '.join(self.class_names)})")
        print(f"训练状态: {'已训练' if self.is_trained else '未训练'}")

        # 打印参数数量
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        print(f"参数数量:")
        print(f"  总参数: {total_params:,}")
        print(f"  可训练参数: {trainable_params:,}")
        print("=" * 60)


# 简化的测试代码
if __name__ == "__main__":
    print("直接测试TransformerFusionModel...")

    # 创建模型
    model = TransformerFusionModel(
        face_dim=13,
        audio_dim=21,
        hr_dim=9,
        num_classes=4,
        hidden_dim=64,
        device="cpu"
    )

    # 测试前向传播
    batch_size = 2
    face_input = torch.randn(batch_size, 13)
    audio_input = torch.randn(batch_size, 21)
    hr_input = torch.randn(batch_size, 9)

    try:
        predictions, contributions = model(face_input, audio_input, hr_input)
        print(f"✓ 前向传播成功")
        print(f"  预测输出形状: {predictions.shape}")
        print(f"  贡献度形状: {contributions['modal_contributions'].shape}")

        # 测试贡献度总和是否为1
        contrib_sum = contributions['modal_contributions'].sum(dim=-1)
        print(f"  贡献度总和: {contrib_sum}")

        # 测试预测函数
        import numpy as np

        results = model.predict(
            face_input.numpy(),
            audio_input.numpy(),
            hr_input.numpy()
        )
        print(f"  预测结果: {results['predictions']}")
        print(f"  置信度: {results['confidence']}")
        print(f"  类别: {results['class_names']}")

        if 'contributions' in results:
            print("  各模态贡献度:")
            for modality, contrib in results['contributions'].items():
                modality_name = {
                    'face': '面部特征',
                    'audio': '语音特征',
                    'hr': '心率特征'
                }.get(modality, modality)
                print(f"    {modality_name}: {contrib:.1f}%")

        print("\n✅ 模型测试通过！")

    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback

        traceback.print_exc()