import script.__init__script

from typing import List, Union

from django.db import models

from apps.chat.models import Sensitive


# 构建前缀树

class Node:
    """
    前缀树节点
    """

    def __init__(self, id, parent_id, char, is_word=False):
        """

        :param id: mysql索引id
        :param parent_id: 父节点id
        :param char: 字符编码
        :param is_word: 是否是个完整的单词，也就是说在前缀树里进行构建过
        """
        self.id = id
        self.parent_id = parent_id
        self.char = char
        self.is_word = is_word
        self.children = dict()

    def find_node(self, char, ) -> Union['TreeNode', None]:
        """
        复杂度为O(len（root.children）)
        :param char:
        :return:
        """
        for key, node in self.children.items():

            if node.char == char:
                return node

        return None

    def replace(self, text, begin, end):
        while begin < end:
            text[begin] = "*"
            begin += 1


class Trie:

    def __init__(
            self, sensitive_words,
            model: models,
            replace_str="*",
    ):
        """

        :param sensitive_words: 敏感词
        :param replace_str: mysql连接对象
        """

        self.replace_str = replace_str
        self.nodes: List[Node] = []
        self.root = Node(1, None, "")
        self.nodes.append(self.root)
        self.sensitive_words = sensitive_words
        self.model = model

    def find_child(self, root: Node, char, node_list: List[Node]) -> Union[None, Node]:
        """
        # 查找是否已经构建过该节点
        :param root:
        :param char:
        :param node_list:
        :return:
        """
        for node in node_list:
            if root.id == node.parent_id and node.char == char:
                return node
        return None

    def truncate_trie_system(self):
        """
        清空树
        :return:
        """
        self.model.objects.all().delete()

    def construction(self):
        """
        构建节点树
        :return:
        """

        for word in self.sensitive_words:
            current_node = self.root
            for char in word:
                node = self.find_child(current_node, char, self.nodes)
                # 不存在更新创建node
                if node is None:
                    node = Node(
                        id=len(self.nodes) + 1,
                        parent_id=current_node.id,
                        char=char
                    )
                    self.nodes.append(node)
                current_node = node
            current_node.is_word = True  # 标记为单词

    def make(self):
        """
        插入节点
        :return:
        """
        # 执行构建树
        self.construction()
        self.truncate_trie_system()
        tree_nodes = []
        for node in self.nodes:
            tree_nodes.append(
                self.model(
                    id=node.id,
                    parentID=node.parent_id,
                    char=node.char,
                    isWord=node.is_word)
            )
        self.model.objects.bulk_create(tree_nodes)

    def print_tree(self, node, prefix="", is_last_child=True, is_root=True):
        branch = "└── " if is_last_child else "├── "
        if is_root:
            print(node.char)
        else:
            print(prefix + branch + node.char)

        children = [n for n in self.nodes if n.parent_id == node.id]
        for idx, child_node in enumerate(children):
            is_last = idx == len(children) - 1
            new_prefix = prefix + ("    " if is_last_child else "│   ")
            self.print_tree(child_node, new_prefix, is_last, False)

    def tree(self):
        root_node = self.nodes[0]
        self.print_tree(root_node)

    def tree_nodes(self):
        # 1. 构建树
        rows = Sensitive.objects.iterator(chunk_size=500)

        tree = {}
        for n in rows:
            node = Node(n.id, n.parentID, n.char, n.isWord)
            p_node = tree.get(n.parentID)
            if p_node:
                p_node.children[n.id] = node
            tree[n.id] = node

        return tree

    def replace(self, text: str):
        cp_text = list(text)
        t_len = len(text)
        # 2. 构建完成
        # 根节点
        tree = self.tree_nodes()
        root = tree.get(1)
        for i in range(t_len):
            trie_node = root.find_node(text[i])
            if trie_node is None:
                continue
            # 找到往，该节点的下面找
            j = 1 + i
            while j < t_len and trie_node is not None:
                # 是一整块单词进行替换
                if trie_node.is_word:
                    trie_node.replace(cp_text, i, j)
                if j == t_len: break
                # 不是一整块继续往下找
                trie_node = trie_node.find_node(text[j])
                j += 1
            if j == t_len and trie_node is not None and trie_node.is_word:
                trie_node.replace(cp_text, i, t_len)
        return "".join(cp_text)


if __name__ == '__main__':

    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "root",
        "database": "test"
    }
    sensitive_words = []
    with open(r"E:\chrome\listLn.txt", "r", encoding="utf-8") as f:
        for line in f:
            sensitive_words.append(line.strip())

    trie = Trie(sensitive_words, Sensitive)
    trie.make()
    # print(trie.replace("+ 群"))
    # trie.tree_nodes()
    # print(trie.replace("+ 群"))
