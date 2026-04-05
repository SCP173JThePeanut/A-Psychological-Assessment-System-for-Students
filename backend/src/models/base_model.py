"""
基础模型类 - 所有模型的基类
"""
import torch
import torch.nn as nn
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional
import json
import pickle


class BaseMentalHealthModel(ABC, nn.Module):
    """心理健康评估模型基类"""

    def __init__(self,
                 face_dim: int = 13,
                 audio_dim: int = 21,
                 hr_dim: int = 9,
                 num_classes: int = 4,
                 device: str = "cpu"):
        """
        初始化模型

        参数:
            face_dim: 面部特征维度
            audio_dim: 语音特征维度
            hr_dim: 心率特征维度
            num_classes: 分类类别数（如：正常、轻度压力、中度压力、重度压力）
            device: 计算设备
        """
        super().__init__()

        self.face_dim = face_dim
        self.audio_dim = audio_dim
        self.hr_dim = hr_dim
        self.num_classes = num_classes
        self.device = device

        # 特征总维度
        self.total_dim = face_dim + audio_dim + hr_dim

        # 类别名称（可根据实际数据修改）
        self.class_names = [
            "正常",  # 0
            "轻度压力",  # 1
            "中度压力",  # 2
            "重度压力"  # 3
        ]

        # 模型配置
        self.config = {
            "face_dim": face_dim,
            "audio_dim": audio_dim,
            "hr_dim": hr_dim,
            "num_classes": num_classes,
            "class_names": self.class_names,
            "model_type": self.__class__.__name__
        }

        # 训练历史
        self.training_history = {
            "train_loss": [],
            "val_loss": [],
            "train_acc": [],
            "val_acc": []
        }

        # 模型状态
        self.is_trained = False
        self.best_val_loss = float('inf')

    @abstractmethod
    def forward(self,
                face_features: torch.Tensor,
                audio_features: torch.Tensor,
                hr_features: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        前向传播

        参数:
            face_features: 面部特征，形状 [batch_size, face_dim]
            audio_features: 语音特征，形状 [batch_size, audio_dim]
            hr_features: 心率特征，形状 [batch_size, hr_dim]

        返回:
            Tuple[predictions, contributions]
            - predictions: 预测结果，形状 [batch_size, num_classes]
            - contributions: 各模态贡献度字典
        """
        pass

    @abstractmethod
    def get_feature_contributions(self,
                                  face_features: torch.Tensor,
                                  audio_features: torch.Tensor,
                                  hr_features: torch.Tensor) -> Dict[str, float]:
        """
        获取各模态特征贡献度

        返回:
            Dict[str, float]: 各模态贡献度百分比
            {"face": 0.35, "audio": 0.25, "hr": 0.40}
        """
        pass

    def predict(self,
                face_features: np.ndarray,
                audio_features: np.ndarray,
                hr_features: np.ndarray,
                return_contributions: bool = True) -> Dict[str, Any]:
        """
        预测心理健康状态

        参数:
            face_features: 面部特征数组
            audio_features: 语音特征数组
            hr_features: 心率特征数组
            return_contributions: 是否返回贡献度

        返回:
            Dict[str, Any]: 包含预测结果的字典
        """
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
            predictions, contributions = self(face_tensor, audio_tensor, hr_tensor)

            # 获取预测类别和概率
            probs = torch.softmax(predictions, dim=-1)
            pred_class = torch.argmax(probs, dim=-1)
            confidence = torch.max(probs, dim=-1).values

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

    def compute_score(self, probabilities):
        """
        根据分类概率计算连续分数 (0-100)
        类别分数映射: 正常=12.5, 轻度=37.5, 中度=62.5, 重度=87.5 (区间中点)
        """
        score_map = torch.tensor([12.5, 37.5, 62.5, 87.5], device=probabilities.device)
        score = torch.sum(probabilities * score_map, dim=-1)
        return score


    def _generate_explanation(self,
                              pred_class: int,
                              confidence: float,
                              contributions: Dict[str, float]) -> str:
        """
        生成可解释性文本

        参数:
            pred_class: 预测类别
            confidence: 置信度
            contributions: 各模态贡献度

        返回:
            str: 解释文本
        """
        class_name = self.class_names[pred_class]

        # 排序贡献度
        sorted_contrib = sorted(
            contributions.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # 构建解释
        explanation_parts = []
        explanation_parts.append(f"预测为{class_name}，置信度{confidence:.1%}")
        explanation_parts.append("主要依据：")

        for modality, contrib in sorted_contrib:
            if contrib > 0.1:  # 只显示显著贡献
                modality_name = {
                    "face": "面部表情",
                    "audio": "语音特征",
                    "hr": "心率信号"
                }.get(modality, modality)

                explanation_parts.append(f"- {modality_name}贡献{contrib:.1%}")

        return "\n".join(explanation_parts)

    def train_step(self,
                   face_features: torch.Tensor,
                   audio_features: torch.Tensor,
                   hr_features: torch.Tensor,
                   labels: torch.Tensor,
                   criterion: nn.Module,
                   optimizer: torch.optim.Optimizer) -> float:
        """
        单个训练步骤

        返回:
            float: 损失值
        """
        self.train()

        # 清空梯度
        optimizer.zero_grad()

        # 前向传播
        predictions, _ = self(face_features, audio_features, hr_features)

        # 计算损失
        loss = criterion(predictions, labels)

        # 反向传播
        loss.backward()

        # 更新参数
        optimizer.step()

        return loss.item()

    def save_model(self, filepath: str):
        """保存模型"""
        save_dict = {
            "model_state_dict": self.state_dict(),
            "config": self.config,
            "training_history": self.training_history,
            "best_val_loss": self.best_val_loss,
            "is_trained": self.is_trained
        }

        torch.save(save_dict, filepath)
        print(f"模型已保存到: {filepath}")

    def load_model(self, filepath: str):
        """加载模型"""
        checkpoint = torch.load(filepath, map_location=self.device)

        self.load_state_dict(checkpoint["model_state_dict"])
        self.training_history = checkpoint.get("training_history", self.training_history)
        self.best_val_loss = checkpoint.get("best_val_loss", float('inf'))
        self.is_trained = checkpoint.get("is_trained", False)

        print(f"模型已从 {filepath} 加载")
        print(f"模型类型: {checkpoint.get('config', {}).get('model_type', 'Unknown')}")
        print(f"训练状态: {'已训练' if self.is_trained else '未训练'}")

    def summary(self):
        """打印模型摘要"""
        print("=" * 60)
        print(f"模型: {self.__class__.__name__}")
        print(f"设备: {self.device}")
        print(f"输入维度:")
        print(f"  面部特征: {self.face_dim}")
        print(f"  语音特征: {self.audio_dim}")
        print(f"  心率特征: {self.hr_dim}")
        print(f"  总维度: {self.total_dim}")
        print(f"输出类别: {self.num_classes} ({', '.join(self.class_names)})")
        print(f"训练状态: {'已训练' if self.is_trained else '未训练'}")

        # 打印参数数量
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        print(f"参数数量:")
        print(f"  总参数: {total_params:,}")
        print(f"  可训练参数: {trainable_params:,}")
        print("=" * 60)