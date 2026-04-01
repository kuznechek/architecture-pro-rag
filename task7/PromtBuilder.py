from langchain_core.prompts import PromptTemplate

class PromtBuilder:
    def __init__(self):
        self.Prompts = self._create_prompts()

    def _create_prompts(self):
        base_prompt = PromptTemplate.from_file("../prompts/base.txt")
        few_shot_prompt = PromptTemplate.from_file("../prompts/few_shot.txt")
        cot_prompt = PromptTemplate.from_file("../prompts/cot.txt")

        return {
            "base":     base_prompt,
            "few_shot": few_shot_prompt,
            "cot":      cot_prompt
        }
