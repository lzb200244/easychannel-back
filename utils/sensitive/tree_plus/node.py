from collections import defaultdict
from typing import Union


class TreeNode:
    """
    前缀树节点
    """

    def __init__(self, value, is_word=False):
        """

        :param id: mysql索引id
        :param parent_id: 父节点id
        :param char: 字符编码
        :param is_word: 是否是个完整的单词，也就是说在前缀树里进行构建过
        """
        self.value = value
        self.is_word = is_word
        self.children = defaultdict(TreeNode)

    def find_node(self, char, ) -> Union['TreeNode', None]:
        """
        时间复杂度:O(1)
        空间复杂度:O(len(root.children))
        :param char:
        :return:
        """
        return self.children.get(char)

    def replace(self, text, begin, end):
        while begin < end:
            text[begin] = "*"
            begin += 1

