"""
Database Models for CraftChain
"""
from datetime import datetime
from bson import ObjectId
from typing import Optional, List, Dict, Any

class User:
    """User model for authentication and profile management"""
    def __init__(self, username: str, password_hash: str, _id: Optional[ObjectId] = None):
        self._id = _id or ObjectId()
        self.username = username
        self.password_hash = password_hash
        self.created_at = datetime.utcnow()
        self.role = "player"  # player, miner, builder, planner
        
    def to_dict(self) -> Dict:
        return {
            "_id": str(self._id),
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at
        }


class CraftingProject:
    """Crafting project model - represents a goal like Beacon or Netherite Sword"""
    def __init__(
        self,
        project_name: str,
        final_item: str,
        required_items: List[Dict[str, Any]],
        owner_id: str,
        world_name: str,
        _id: Optional[ObjectId] = None
    ):
        self._id = _id or ObjectId()
        self.project_name = project_name
        self.final_item = final_item
        self.required_items = required_items  # [{"name": "item", "quantity": 1, "completed": 0}, ...]
        self.owner_id = owner_id
        self.world_name = world_name  # Minecraft world this project belongs to
        self.collaborators = [owner_id]  # Users who can contribute
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.status = "active"  # active, completed
        self.contributions = []  # List of contribution IDs
        
    def to_dict(self) -> Dict:
        return {
            "_id": str(self._id),
            "project_name": self.project_name,
            "final_item": self.final_item,
            "required_items": self.required_items,
            "owner_id": self.owner_id,
            "world_name": self.world_name,
            "collaborators": self.collaborators,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "progress": self.calculate_progress()
        }
    
    def calculate_progress(self) -> float:
        """Calculate overall project progress as percentage"""
        if not self.required_items:
            return 0.0
        
        total_required = sum(item.get("quantity", 0) for item in self.required_items)
        total_completed = sum(item.get("completed", 0) for item in self.required_items)
        
        return (total_completed / total_required * 100) if total_required > 0 else 0.0


class Contribution:
    """Track individual contributions to a project"""
    def __init__(
        self,
        project_id: str,
        user_id: str,
        item_name: str,
        quantity: int,
        contribution_type: str,  # "collected" or "crafted"
        _id: Optional[ObjectId] = None
    ):
        self._id = _id or ObjectId()
        self.project_id = project_id
        self.user_id = user_id
        self.item_name = item_name
        self.quantity = quantity
        self.contribution_type = contribution_type
        self.created_at = datetime.utcnow()
        self.verified = False
        
    def to_dict(self) -> Dict:
        return {
            "_id": str(self._id),
            "project_id": self.project_id,
            "user_id": self.user_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "contribution_type": self.contribution_type,
            "created_at": self.created_at,
            "verified": self.verified
        }


class Enchantment:
    """Enchantments for crafted items (brownie points feature)"""
    def __init__(
        self,
        name: str,
        level: int,
        effect: str,
        resource_cost_multiplier: float = 1.0,
        _id: Optional[ObjectId] = None
    ):
        self._id = _id or ObjectId()
        self.name = name  # Efficiency, Unbreaking, Fortune, Sharpness
        self.level = level  # 1-5 typically
        self.effect = effect
        self.resource_cost_multiplier = resource_cost_multiplier
        
    def to_dict(self) -> Dict:
        return {
            "_id": str(self._id),
            "name": self.name,
            "level": self.level,
            "effect": self.effect,
            "resource_cost_multiplier": self.resource_cost_multiplier
        }


class EnchantedItem:
    """Items with enchantments attached"""
    def __init__(
        self,
        project_id: str,
        item_name: str,
        enchantments: List[Enchantment],
        base_quantity: int,
        _id: Optional[ObjectId] = None
    ):
        self._id = _id or ObjectId()
        self.project_id = project_id
        self.item_name = item_name
        self.enchantments = [e.to_dict() for e in enchantments]
        self.base_quantity = base_quantity
        self.adjusted_quantity = self.calculate_adjusted_quantity()
        self.created_at = datetime.utcnow()
        
    def calculate_adjusted_quantity(self) -> int:
        """Calculate quantity needed accounting for enchantment costs"""
        multiplier = 1.0
        for enchant in self.enchantments:
            multiplier *= enchant.get("resource_cost_multiplier", 1.0)
        return int(self.base_quantity * multiplier)
    
    def to_dict(self) -> Dict:
        return {
            "_id": str(self._id),
            "project_id": self.project_id,
            "item_name": self.item_name,
            "enchantments": self.enchantments,
            "base_quantity": self.base_quantity,
            "adjusted_quantity": self.adjusted_quantity,
            "created_at": self.created_at
        }


class InventoryItem:
    """Inventory item model - represents an item stored in world inventory"""
    def __init__(
        self,
        owner_id: str,
        world_name: str,
        item_name: str,
        quantity: int,
        _id: Optional[ObjectId] = None
    ):
        self._id = _id or ObjectId()
        self.owner_id = owner_id
        self.world_name = world_name
        self.item_name = item_name
        self.quantity = quantity
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
    def to_dict(self) -> Dict:
        return {
            "_id": str(self._id),
            "owner_id": self.owner_id,
            "world_name": self.world_name,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
