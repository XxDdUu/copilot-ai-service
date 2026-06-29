from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkingService:

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=[
                "\n\n",
                "\n",
                ". ",
                "? ",
                "! ",
                " ",
                ""
            ]
        )

    def chunk_text(self, text: str):
        return self.splitter.split_text(text)