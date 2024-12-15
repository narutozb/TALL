from typing import Optional

from maya import cmds


def get_new_name(obj_path, suffix: str = None, prefix: str = None):
    '''
    获取新的短名。 例如：|group1|group2|obj  =>  obj_renamed
    :param prefix:  prefix_
    :param obj_path: |group1|group2|obj
    :param suffix:  _suffix
    :return:  obj_renamed
    '''
    if not prefix:
        prefix = ''
    if not suffix:
        suffix = ''

    base_name = obj_path.split('|')[-1]  # 获取物体的名称部分
    return prefix + base_name + suffix


def get_sorted_selected_objects():
    # 获取选中对象并按路径长度排序
    selected_objects = cmds.ls(selection=True, long=True)
    selected_objects.sort(key=lambda x: x.count('|'), reverse=True)
    return selected_objects


def add_prefix_by_selected_objects(prefix: str = None, suffix: str = None):
    if not prefix and not suffix:
        print("请提供前缀或后缀")
        return

    # 批量重命名
    for obj in get_sorted_selected_objects():
        new_name = get_new_name(obj, suffix=suffix, prefix=prefix)
        if cmds.objExists(obj):
            cmds.rename(obj, new_name)


'''
添加前缀
添加后缀
全部大写
全部小写
替换特定字符串
'''
