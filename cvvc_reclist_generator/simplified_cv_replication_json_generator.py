"""generate a alias copy json config for Kira Oto Tool Box in case of simplified cv is used."""

import json, time, os
from lib2to3.pygram import pattern_symbols
from typing import Iterable, Optional


JSON_TEMPLATE = {
    "content": {
        "behaviorCopy": True,
        "behaviorReplace": False,
        "opStrategy": 1,
        "rules": [],
    },
    "lastModified": "",
    "name": "",
    "version": 2,
}


class CvReplicationJsonGenerator:
    """to generate a json config"""

    def __init__(
        self,
        rules: Optional[list[dict]] = None,
        is_copy: bool = True,
        op_strategy: int = 1,
    ) -> None:
        self.json_config = JSON_TEMPLATE

        self.json_config["content"]["rules"] = rules

        if not is_copy:
            self.json_config["content"]["behaviorCopy"] = False
            self.json_config["content"]["behaviorReplace"] = True

        if op_strategy not in (0, 1, 2) and is_copy:
            raise AttributeError("in copy mode only 0, 1, 2 is valid for op_strategy")

        if op_strategy not in (0, 1) and not is_copy:
            raise AttributeError("in replace mode only 0, 1 is valid for op_strategy")

        self.json_config["content"]["opStrategy"] = op_strategy

    @staticmethod
    def new_rule(
        match_pattern: str, target_pattern: str, strategy: int = 0
    ) -> dict[str, str | int]:
        return {
            "matchPattern": match_pattern,
            "strategy": strategy,
            "targetPattern": target_pattern,
        }

    @staticmethod
    def get_json_rules(
        rules: Iterable[tuple[str, str]],
        strategy: int = 0,
        patterns: Optional[list[str]] = None,
    ) -> list[dict]:
        """read a iterable of tuple that contain match pattern and target pattern,
        and return a json str.

        Args:
            rules (Iterable[tuple[str, str]]): tuple[match pattern, target pattern]
        """

        json_rules = []
        for rule in rules:
            json_rules.append(
                CvReplicationJsonGenerator.new_rule(rule[0], rule[1], strategy)
            )

            if patterns:
                for pattern in patterns:
                    match_pattern = pattern.replace("{}", rule[0])
                    target_pattern = pattern.replace("{}", rule[1])
                    
                    if match_pattern == rule[0]:
                        continue

                    json_rules.append(
                        CvReplicationJsonGenerator.new_rule(
                            match_pattern, target_pattern, strategy
                        )
                    )

        return json_rules

    def add_rules(self, rules: list[dict]):
        """add multiple rules"""

        self.json_config["content"]["rules"].extend(rules)

    def add_rule(self, rule: dict):
        """add one single rule"""

        self.json_config["content"]["rules"].append(rule)

    def save_json(
        self, file_name: str = "simplified cv replication.json", file_path: str = "./"
    ):
        """add last modified time, file name and save json config file"""
        last_modified_time = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
        self.json_config["lastModified"] = last_modified_time
        self.json_config["name"] = file_name

        json_path = os.path.join(file_path, file_name)

        with open(json_path, mode="w", encoding="utf-8") as fp:
            json.dump(self.json_config, fp, indent=4)


if __name__ == "__main__":
    rules = [("a", "ao"), ("- a", "- ao"), ("ba", "bao"), ("- ba", "- bao")]
    json_rules = CvReplicationJsonGenerator.get_json_rules(rules)
    json_generator = CvReplicationJsonGenerator(json_rules)
    json_generator.save_json()
