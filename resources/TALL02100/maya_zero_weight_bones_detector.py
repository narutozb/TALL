"""
Maya Zero Weight Bones Detector
用于检测和分析Maya场景中的骨骼权重情况

主要用途：
1. FBX导出前的清理工作
   - 识别可以安全移除的零权重骨骼
   - 帮助减少导出文件的大小
   - 避免将不必要的骨骼导出到游戏引擎

2. 场景优化和维护
   - 快速定位可能不需要的骨骼
   - 协助技术美术进行场景清理
   - 优化绑定结构

使用方法：
1. 选择要检查的mesh物体
2. 运行脚本
3. 查看分析结果：
   - 零权重骨骼：已添加到skinCluster但没有实际权重的骨骼
   - 未绑定骨骼：在骨骼层级中但未添加到skinCluster的骨骼
"""

import dataclasses
from typing import List, Dict, Optional, Set

import maya.cmds as cmds


@dataclasses.dataclass
class ZeroWeightJoint:
    """
    存储骨骼分析结果的数据类

    Attributes:
        name (str): 骨骼的名称
        parent (str, optional): 父骨骼的名称，如果是根骨骼则为None
        has_skin_cluster (bool): 是否已添加到skinCluster
            - True: 骨骼在skinCluster中但权重为0
            - False: 骨骼不在skinCluster中
    """
    name: str
    parent: Optional[str] = None
    has_skin_cluster: bool = True


def get_joint_hierarchy(root_joint: str) -> List[str]:
    """
    获取从指定根骨骼开始的所有子骨骼

    性能优化：
    - 使用 listRelatives 的 allDescendents 参数一次性获取所有子骨骼
    - 避免递归调用
    - 使用类型过滤减少不必要的节点查询

    Args:
        root_joint: 根骨骼的名称

    Returns:
        包含所有骨骼名称的列表
    """
    joints = cmds.listRelatives(
        root_joint,
        allDescendents=True,  # 使用allDescendents代替ad，更明确
        type='joint',
        fullPath=True  # 使用完整路径避免命名冲突
    ) or []
    joints.append(root_joint)
    return joints


def get_bones_info(mesh_name: str, threshold: float = 0.00001) -> List[ZeroWeightJoint]:
    """
    分析指定mesh的骨骼情况，识别零权重和未绑定的骨骼

    性能优化：
    - 使用集合(Set)进行骨骼列表的比较
    - 批量获取权重数据
    - 缓存中间结果避免重复查询

    :param mesh_name: 要分析的mesh名称
    :param threshold:  零权重骨骼阈值
    :return: 包含所有问题骨骼信息的列表

    :raises 当mesh不存在、无效或未绑定骨骼时抛出
    """
    results: List[ZeroWeightJoint] = []

    # 验证输入
    if not cmds.objExists(mesh_name):
        raise RuntimeError(f"找不到物体: {mesh_name}")

    # 获取mesh shape节点（使用完整路径）
    mesh_shapes = cmds.listRelatives(
        mesh_name,
        shapes=True,
        type='mesh',
        fullPath=True
    )
    if not mesh_shapes:
        raise RuntimeError(f"{mesh_name} 不是一个有效的mesh物体")

    # 获取蒙皮变形器
    skin_cluster = cmds.listConnections(
        mesh_shapes[0],
        type='skinCluster',
        source=True,
        destination=False
    )
    if not skin_cluster:
        raise RuntimeError(
            f"在 {mesh_name} 上没有找到蒙皮变形器(Skin Cluster)。\n"
            "请确保该mesh已经绑定了骨骼。\n"
            "你可以通过选择mesh和骨骼，然后使用 Skin -> Bind Skin 来创建蒙皮。"
        )

    # 获取influence骨骼（使用集合提高查找效率）
    influences = set(cmds.skinCluster(skin_cluster[0], q=True, inf=True) or [])
    if not influences:
        raise RuntimeError("未找到任何绑定的骨骼")

    # 获取根骨骼
    root_joint = next(iter(influences))  # 获取任意一个骨骼作为起点
    while True:
        parent = cmds.listRelatives(root_joint, parent=True, type='joint')
        if not parent:
            break
        root_joint = parent[0]

    # 获取并缓存所有骨骼
    all_joints = get_joint_hierarchy(root_joint)

    # 创建父骨骼查找缓存
    parent_cache = {
        joint: cmds.listRelatives(joint, parent=True, type='joint')[0]
        if cmds.listRelatives(joint, parent=True, type='joint')
        else None
        for joint in all_joints
    }

    # 使用集合存储非零权重骨骼
    nonzero_weight_joints: Set[str] = set()

    # 批量获取权重数据
    for vtx_idx in range(cmds.polyEvaluate(mesh_name, v=True)):
        weights = cmds.skinPercent(
            skin_cluster[0],
            f"{mesh_name}.vtx[{vtx_idx}]",
            q=True,
            v=True,
            normalize=True
        )
        for inf_idx, weight in enumerate(weights):
            if weight > threshold:
                nonzero_weight_joints.add(list(influences)[inf_idx])

    # 处理所有骨骼
    for joint in all_joints:
        if joint in influences:
            if joint not in nonzero_weight_joints:
                results.append(ZeroWeightJoint(
                    name=joint,
                    parent=parent_cache[joint],
                    has_skin_cluster=True
                ))
        else:
            results.append(ZeroWeightJoint(
                name=joint,
                parent=parent_cache[joint],
                has_skin_cluster=False
            ))

    return results


def main() -> Optional[List[ZeroWeightJoint]]:
    """
    主函数：分析当前选中mesh的骨骼情况并输出结果

    Returns:
        如果成功，返回问题骨骼列表；如果失败，返回空列表
    """
    selection = cmds.ls(sl=True, type='transform')
    if not selection:
        raise RuntimeError("请先选择一个mesh物体")

    try:
        results = get_bones_info(selection[0])

        print(f"\n===== {selection[0]} 的骨骼分析结果 =====")

        # 按类型分组并输出结果
        zero_weight_bones = [j for j in results if j.has_skin_cluster]
        no_skin_bones = [j for j in results if not j.has_skin_cluster]

        print(f"\n1. 零权重骨骼 ({len(zero_weight_bones)}个):")
        if zero_weight_bones:
            for joint in zero_weight_bones:
                parent_info = f" (父骨骼: {joint.parent})" if joint.parent else ""
                print(f"- {joint.name}{parent_info}")
        else:
            print("- 没有发现零权重骨骼")

        print(f"\n2. 没有skinCluster的骨骼 ({len(no_skin_bones)}个):")
        if no_skin_bones:
            for joint in no_skin_bones:
                parent_info = f" (父骨骼: {joint.parent})" if joint.parent else ""
                print(f"- {joint.name}{parent_info}")
        else:
            print("- 所有骨骼都已添加到skinCluster中")

        return results

    except RuntimeError as e:
        print(f"\n错误: {str(e)}")
        return []


if __name__ == "__main__":
    main()
