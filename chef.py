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
    ingredient_type: str


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
        self.original_ingr = None
        self.ingr = None
        self.ingredients_names = []
        self.original_method = None
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
                self.original_ingr = self.comment
                self.comment = None
            else:
                print("Comment: ", self.comment.group())
                self.script = re.sub(re.escape(self.comment.group()), "", self.script)

        ############################################################################
        # now we can parse the ingredients
        ############################################################################
        if self.original_ingr is None:
            self.original_ingr = re.match("(.*?)\n\n", self.script, re.DOTALL)
            if self.original_ingr is None:
                raise ValueError(
                    "Invalid script format, please provide a valid recipe (no ingredients)"
                )
            first_line = self.original_ingr.group().split(" ")[0]
            if "Ingredients" not in first_line:
                raise ValueError(
                    "Invalid script format, please provide a valid recipe (no ingredients)"
                )

        self.script = re.sub(re.escape(self.original_ingr.group()), "", self.script)
        print(f"Ingredients: {self.original_ingr.group()}")

        self.parse_ingredients(self.original_ingr.group())

        ############################################################################
        # now we can parse the method, note that we can also have before the method
        # the cook time and oven temperature, so we need to check for that
        ############################################################################
        method = re.match("(.*?)\n\n", self.script, re.DOTALL)

        if method is not None:
            first_line = method.group().split(" ")[0]
            if "Method" in first_line:
                self.original_method = method
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
                    self.original_method = method
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

        if self.original_method is None:
            self.original_method = re.match("(.*?)\n\n", self.script, re.DOTALL)
            if self.original_method is None:
                raise ValueError(
                    "Invalid script format, please provide a valid recipe (no method)"
                )
            first_line = self.original_method.group().split(" ")[0]
            if "Method" not in first_line:
                raise ValueError(
                    "Invalid script format, please provide a valid recipe (no method)"
                )

        self.script = re.sub(re.escape(self.original_method.group()), "", self.script)
        print(f"Method: {self.original_method.group()}")

        self.parse_method(self.original_method.group())

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

    def parse_ingredients(self, ingredients):
        """
        example list

        Ingredients.
        111 g sugar
        12 ml hot water

        [initial-value] [[measure-type] measure] ingredient-name

        1. The initial-value is a positive integer. (Required)
        2. The measure-type is one of the following: heaped | level : These indicate that the measure is dry. (Optional)
        3. The measure is one of the following... (Optional)
            g | kg | pinch[es] : These always indicate dry measures.
            ml | l | dash[es] : These always indicate liquid measures.
            cup[s] | teaspoon[s] | tablespoon[s] : These indicate measures which may be either dry or liquid.
        4. The ingredient-name is any string of characters. (Required)
        """

        ingredients = ingredients.split("\n")

        measure_types = set(["heaped", "level"])

        measures = set(
            [
                "g",
                "kg",
                "pinch",
                "pinches",
                "ml",
                "l",
                "dash",
                "dashes",
                "cup",
                "cups",
                "teaspoon",
                "teaspoons",
                "tablespoon",
                "tablespoons",
            ]
        )

        parsed_ingredients = []

        for ingredient in ingredients:
            if ingredient == "Ingredients." or ingredient == "":
                continue

            ingredient = ingredient.split(" ")
            initial_value = ingredient[0]
            if not initial_value.isdigit():
                raise ValueError(
                    "Invalid ingredient format, initial value must be a number"
                )
            measure = ingredient[1]
            if measure not in measures:
                measure = None
                ingredient_name = " ".join(ingredient[1:])
                if ingredient_name == "" or ingredient_name in measure_types:
                    raise ValueError(
                        "Invalid ingredient format, ingredient name must be provided"
                    )
            else:
                measure_type = ingredient[2]
                if measure_type not in measure_types:
                    measure_type = None
                    ingredient_name = " ".join(ingredient[2:])
                    self.ingredients_names.append(ingredient_name)
                else:
                    ingredient_name = " ".join(ingredient[3:])
                    self.ingredients_names.append(ingredient_name)

            parsed_ingredients.append(
                {
                    "initial_value": initial_value,
                    "measure": measure,
                    "measure_type": measure_type,
                    "ingredient_name": ingredient_name,
                }
            )

        self.ingr = parsed_ingredients

    def parse_method(self, method):
        """
        example list

        Method.
        method-instruction.
        """
        instruction_set = set(
            [
                "Take",
                "Put",
                "Fold",
                "Add",
                "Remove",
                "Combine",
                "Divide",
                "Liquefy",
                "Liquify",
                "Stir",
                "Mix",
                "Clean",
                "Pour",
                "Serve",
                "Refrigerate",
                "Verb",
                "Set",
            ]
        )

        instructions = method.split("\n")

        parsed_instructions = []

        for instruction in instructions:
            if instruction == "Method." or instruction == "":
                continue

            instruction = instruction.split(" ")
            verb = instruction[0]
            if verb not in instruction_set:
                raise ValueError(
                    "Invalid instruction format, instruction must be a valid instruction",
                    verb,
                )

            parsed_instructions.append(" ".join(instruction))

        self.method = parsed_instructions

    # DO NOT IMPLEMENT THIS FUNCTION FOR NOW
    def parse_auxiliary_recipe(self, recipe):
        pass

    def execute_script(self):
        pass


def main():
    script = sys.argv[1]
    with open(script, "r") as f:
        script = f.read()

    chef = Chef(script)
    chef.parse_script()


if __name__ == "__main__":
    main()
