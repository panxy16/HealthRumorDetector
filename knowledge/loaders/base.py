class BaseLoader:
    def load(self, path: str) -> str:
        """
        输入：任意文档路径
        输出：Markdown 字符串
        """
        raise NotImplementedError
