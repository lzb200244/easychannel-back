import threading

import script.__init__script

from django.db import models

from apps.chat.models import Sensitive
from utils.sensitive.tree_plus.node import TreeNode


# 构建前缀树


class Tree:
    # 敏感词放入内存里，以免每次都需要从db进行查询。但是敏感词不能过多
    sensitive_words_in_memory = []
    lock = threading.Lock()

    def __init__(
            self,
            model: models,
            replace_str="*",
    ):
        """

        :param model: 模型对象
        :param replace_str:
        """

        self.replace_str = replace_str
        self.root = TreeNode(" ", is_word=True)
        self.model = model
        if not getattr(self.model, "word"):
            raise Exception("model没有word属性,需要使用word来进行构建前缀树")
        if not issubclass(self.model, models.Model):
            raise Exception("model必须是models.Model的子类")

    def truncate_trie_system(self):
        """
        清空树
        :return:
        """
        self.model.objects.all().delete()

    def write_sensitive_to_mysql(self, sensitive_words):
        """
        敏感词写入mysql
        """
        # 1.执行构建树
        self.truncate_trie_system()
        tree_words = []
        # 2.持久化敏感词
        for word in sensitive_words:
            tree_words.append(
                self.model(
                    word=word
                )
            )
        self.model.objects.bulk_create(tree_words)

    # 从mysql读取数据构建前缀树
    def construction(self):
        """
        构建节点树
        :return:
        """
        if len(self.sensitive_words_in_memory) == 0:
            self.lock.acquire()
            if len(self.sensitive_words_in_memory) == 0:
                self.read_from_mysql()
            self.lock.release()
        for word in self.sensitive_words_in_memory:
            root = self.root
            for char in word:
                node = root.children.get(char)
                if node is None:
                    node = TreeNode(
                        value=char
                    )
                    root.children[char] = node
                root = node
            # 标记为完整的一个单词
            root.is_word = True

    def read_from_mysql(self):
        for word_obj in self.model.objects.iterator():
            self.sensitive_words_in_memory.append(word_obj.word)

    def replace(self, text: str) -> tuple[list, str]:
        """

        :param text: 存在敏感词的字符串
        :return: tuple[list, str] 返回过滤掉的敏感词, 已经进行过敏感词替换的字符串
        """
        # 1. 执行构建树
        self.construction()
        # 2. 替换
        cp_text = list(text)
        t_len = len(text)
        root = self.root
        replaced_text = []
        for i in range(t_len):
            trie_node = root.find_node(text[i])
            if trie_node is None:
                continue
            # 找到往，该节点的下面找
            j = 1 + i
            while j < t_len and trie_node is not None:
                # 是一整块单词进行替换
                if trie_node.is_word:
                    # 替换
                    trie_node.replace(cp_text, i, j)
                    # 敏感词记录
                    replaced_text.append(text[i:j])
                if j == t_len:
                    break
                # 不是一整块继续往下找
                trie_node = trie_node.find_node(text[j])
                j += 1
            if j == t_len and trie_node is not None and trie_node.is_word:
                trie_node.replace(cp_text, i, t_len)
                replaced_text.append(text[i:])  # 敏感词记录
        return replaced_text, "".join(cp_text)

    def _print_node(self, node, indent="", is_last=True):
        """
        打印前缀树
        :param node:
        :param indent:缩进
        :param is_last:
        :return:
        """
        branch = "│   "
        joint = "└── "
        if not is_last:
            joint = "├── "
        print(indent + joint + node.value)

        child_count = len(node.children)
        for index, (char, child_node) in enumerate(node.children.items()):
            is_last_child = index == child_count - 1
            self._print_node(child_node, indent + ("\t" if is_last else branch), is_last_child)

    def print_structure(self):
        print("root")
        self._print_node(self.root, is_last=True)


tree_prefix = Tree(Sensitive)

if __name__ == '__main__':
    filters, new_str = tree_prefix.replace("cnm +++")
    tree_prefix.print_structure()
