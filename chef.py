import re
from dataclasses import dataclass
import sys

"""
CHEF INTERPRETER WRITTEN IN PYTHON, FOR MORE INFORMATION ON HOW THE LANGUAGE WORKS, CONSULT THE README FILE
"""


@dataclass
class Ingredient:
    name: str
    value: float
    measure: str
    measure_type: str


@dataclass
class Recipe:
    name: str
    ingredients: list[Ingredient]
    method: list[str]
    comment: str
    cook_time: str
    oven_temp: str
    serves: str
    auxiliary_recipes: list[str]


@dataclass
class MixingBowl:
    name: str
    ingredients: list[Ingredient]  # this acts as a stack


@dataclass
class BakingDish:
    name: str
    ingredients: list[Ingredient]  # this acts as a stack


class Chef:
    def __init__(self, script):
        self.script = script
        self.original_script = script
        self.mixing_bowls = []
        self.baking_dishes = []
        self.recipe_name = None
        self.comment = None
        self.ingr = None
        self.method = None
        self.cook_time = None
        self.oven_temp = None
        self.serves = None
        self.auxiliary_recipes = []

    def parse_script(self):
        ############################################################################
        # the first line of the script should be the title of the recipe
        ############################################################################
        self.recipe_name = re.match("(.*?)\.\n\n", self.script)
        if self.recipe_name is None:
            raise ValueError("Invalid script format, please provide a valid recipe")

        self.script = re.sub(self.recipe_name.group(), "", self.script)
        print(f"Recipe: {self.recipe_name.group()}")

        ############################################################################
        # the next thing we could have is a comment or the ingredients
        ############################################################################
        self.comment = re.match("(.*?)\n\n", self.script, re.DOTALL)

        if self.comment is not None:
            first_line = self.comment.group().split(" ")[0]
            if "Ingredients" in first_line:
                self.ingr = self.comment
                self.comment = None
            else:
                print("Comment: ", self.comment.group())
                self.script = re.sub(re.escape(self.comment.group()), "", self.script)

        ############################################################################
        # now we can parse the ingredients
        ############################################################################
        if self.ingr is None:
            self.ingr = re.match("(.*?)\n\n", self.script, re.DOTALL)
            if self.ingr is None:
                raise ValueError(
                    "Invalid script format, please provide a valid recipe (no ingredients)"
                )
            first_line = self.ingr.group().split(" ")[0]
            if "Ingredients" not in first_line:
                raise ValueError(
                    "Invalid script format, please provide a valid recipe (no ingredients)"
                )

        self.script = re.sub(re.escape(self.ingr.group()), "", self.script)
        print(f"Ingredients: {self.ingr.group()}")
        # TODO: parse ingredients (check that the format is correct)

        ############################################################################
        # now we can parse the method, note that we can also have before the method
        # the cook time and oven temperature, so we need to check for that
        ############################################################################
        method = re.match("(.*?)\n\n", self.script, re.DOTALL)

        if method is not None:
            first_line = method.group().split(" ")[0]
            if "Method" in first_line:
                self.method = method
                method = None
            elif "Cooking" in first_line:
                self.cook_time = method
                method = None
            elif "Pre-heat" in first_line:
                self.oven_temp = method
                method = None
            else:
                raise ValueError(
                    "Invalid script format, please provide a valid recipe (no method)"
                )

        if self.cook_time is not None:
            print("Cooking Time: ", self.cook_time.group())
            self.script = re.sub(re.escape(self.cook_time.group()), "", self.script)

            method = re.match("(.*?)\n\n", self.script, re.DOTALL)
            if method is not None:
                first_line = method.group().split(" ")[0]
                if "Method" in first_line:
                    self.method = method
                    method = None
                elif "Pre-heat" in first_line:
                    self.oven_temp = method
                    method = None
                else:
                    raise ValueError(
                        "Invalid script format, please provide a valid recipe (no method)"
                    )

        if self.oven_temp is not None:
            print("Oven Temperature: ", self.oven_temp.group())
            self.script = re.sub(re.escape(self.oven_temp.group()), "", self.script)

        if self.method is None:
            self.method = re.match("(.*?)\n\n", self.script, re.DOTALL)
            if self.method is None:
                raise ValueError(
                    "Invalid script format, please provide a valid recipe (no method)"
                )
            first_line = self.method.group().split(" ")[0]
            if "Method" not in first_line:
                raise ValueError(
                    "Invalid script format, please provide a valid recipe (no method)"
                )

        self.script = re.sub(re.escape(self.method.group()), "", self.script)
        print(f"Method: {self.method.group()}")

        # TODO: parse method

        ############################################################################
        # Parse the serves
        ############################################################################
        serves = re.match("(.*?)\n\n", self.script, re.DOTALL)

        if serves is not None:
            first_line = serves.group().split(" ")[0]
            if "Serves" in first_line:
                self.serves = serves
            else:
                raise ValueError(
                    "Invalid script format, please provide a valid recipe (no serves)"
                )
        else:
            raise ValueError(
                "Invalid script format, please provide a valid recipe (no serves)"
            )

        print("Serves: ", self.serves.group())
        self.script = re.sub(re.escape(self.serves.group()), "", self.script)

        ############################################################################
        # Parse auxiliary recipes (if any)
        ############################################################################
        aux = re.match("(.*?)\n\n", self.script, re.DOTALL)

        """
        auxiliary recipes are optional, and consists of 3 elements:
        - the name of the recipe 
        - the ingredients 
        - the method
        """
        if aux is None:
            print("No auxiliary recipes")
        else:
            while True:
                # get the name of the recipe
                recipe_name = re.match("(.*?)\n\n", self.script, re.DOTALL)
                if recipe_name is None:
                    break
                print("Auxiliary Recipe: ", recipe_name.group())
                self.script = re.sub(re.escape(recipe_name.group()), "", self.script)

                # get the ingredients
                ingredients = re.match("(.*?)\n\n", self.script, re.DOTALL)
                if ingredients is None:
                    raise ValueError(
                        "Invalid script format, please provide a valid recipe (no ingredients)"
                    )
                print("Ingredients: ", ingredients.group())
                self.script = re.sub(re.escape(ingredients.group()), "", self.script)

                print("Script", self.script)

                # get the Method
                method = re.match("(.*?)\n\n", self.script, re.DOTALL)
                if method is None:
                    raise ValueError(
                        "Invalid script format, please provide a valid recipe (no method)"
                    )
                print("Method: ", method.group())
                self.script = re.sub(re.escape(method.group()), "", self.script)

                # TODO: parse auxiliary recipe

                self.auxiliary_recipes.append(
                    Recipe(
                        recipe_name.group(),
                        ingredients.group(),
                        method.group(),
                        "",
                        "",
                        "",
                        "",
                        [],
                    )
                )


def main():
    script = sys.argv[1]
    with open(script, "r") as f:
        script = f.read()

    chef = Chef(script)
    chef.parse_script()


if __name__ == "__main__":
    main()
