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
    ingredient_type: str  # dry or liquid


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
        self.number_of_mixing_bowls = 1
        self.baking_dishes = []
        self.number_of_baking_dishes = 1
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

    # LEXICAL ANALYSIS
    def parse_script(self):
        ############################################################################
        # the first line of the script should be the title of the recipe
        ############################################################################
        self.recipe_name = re.match("(.*?)\.\n\n", self.script)
        if self.recipe_name is None:
            raise ValueError("Invalid script format, please provide a valid recipe")

        self.script = re.sub(self.recipe_name.group(), "", self.script)
        # print(f"Recipe: {self.recipe_name.group()}")

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
                # print("Comment: ", self.comment.group())
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
        # print(f"Ingredients: {self.original_ingr.group()}")

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
            # print("Cooking Time: ", self.cook_time.group())
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
            # print("Oven Temperature: ", self.oven_temp.group())
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
        # print(f"Method: {self.original_method.group()}")

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

        # print("Serves: ", self.serves.group())
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
            # print("No auxiliary recipes")
            pass
        else:
            while True:
                # get the name of the recipe
                recipe_name = re.match("(.*?)\n\n", self.script, re.DOTALL)
                if recipe_name is None:
                    break
                # print("Auxiliary Recipe: ", recipe_name.group())
                self.script = re.sub(re.escape(recipe_name.group()), "", self.script)

                # get the ingredients
                ingredients = re.match("(.*?)\n\n", self.script, re.DOTALL)
                if ingredients is None:
                    raise ValueError(
                        "Invalid script format, please provide a valid recipe (no ingredients)"
                    )
                # print("Ingredients: ", ingredients.group())
                self.script = re.sub(re.escape(ingredients.group()), "", self.script)

                # print("Script", self.script)

                # get the Method
                method = re.match("(.*?)\n\n", self.script, re.DOTALL)
                if method is None:
                    raise ValueError(
                        "Invalid script format, please provide a valid recipe (no method)"
                    )
                # print("Method: ", method.group())
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

        dry_measures = set(
            [
                "g",
                "kg",
                "pinch",
                "pinches",
            ]
        )

        liquid_measures = set(["ml", "l", "dash", "dashes"])

        general_measures = set(
            [
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
            if measure not in dry_measures.union(liquid_measures).union(
                general_measures
            ):
                measure = None
                ingredient_name = " ".join(ingredient[1:])
                self.ingredients_names.append(ingredient_name)
                if ingredient_name == "" or ingredient_name in measure_types:
                    raise ValueError(
                        "Invalid ingredient format, ingredient name must be provided"
                    )
                ingredient_type = "dry"
            else:
                measure_type = ingredient[2]
                if measure in dry_measures:
                    ingredient_type = "dry"
                if measure in liquid_measures:
                    ingredient_type = "liquid"
                if measure in general_measures:
                    ingredient_type = "dry or liquid"
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
                    "ingredient_type": ingredient_type,
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

    def prepare_mixing_bowls(self, instruction):
        # check if there are any more mixing bowls
        if instruction.group(2) is None:
            if self.number_of_mixing_bowls > 1:
                raise ValueError(
                    "A mixing bowl may not be used without a number if other mixing bowls have been used with a number."
                )
            else:
                mixing_bowl_number = 1
                if len(self.mixing_bowls) == 0:
                    self.mixing_bowls.append(MixingBowl("Mixing Bowl 1", []))

        # check that we provide with enough mixing bowls
        if instruction.group(2) is not None:
            self.number_of_mixing_bowls = int(instruction.group(2))
            mixing_bowl_number = self.number_of_mixing_bowls
            if self.number_of_mixing_bowls > len(self.mixing_bowls):
                for i in range(len(self.mixing_bowls), self.number_of_mixing_bowls):
                    self.mixing_bowls.append(MixingBowl(f"Mixing Bowl {i+1}", []))

        return mixing_bowl_number

    def prepare_baking_dishes(self, instruction):
        # check if there are any more baking dishes
        if instruction.group(2) is None:
            if self.number_of_baking_dishes > 1:
                raise ValueError(
                    "A baking dish may not be used without a number if other baking dishes have been used with a number."
                )
            else:
                baking_dish_number = 1
                if len(self.baking_dishes) == 0:
                    self.baking_dishes.append(BakingDish("Baking Dish 1", []))

        # check that we provide with enough baking dishes
        if instruction.group(2) is not None:
            self.number_of_baking_dishes = int(instruction.group(2))
            baking_dish_number = self.number_of_baking_dishes
            if self.number_of_baking_dishes > len(self.baking_dishes):
                for i in range(len(self.baking_dishes), self.number_of_baking_dishes):
                    self.baking_dishes.append(BakingDish(f"Baking Dish {i+1}", []))

        return baking_dish_number

    def check_ingredient_is_valid(self, ingredient):
        if ingredient not in self.ingredients_names:
            raise ValueError(
                f"Ingredient {ingredient} not found in the list of ingredients"
            )

    def execute_script(self):
        # Execute the instructions
        print(self.ingr)
        for instruction in self.method:
            ############################################################################
            # PUT INGREDIENT INTO MIXING BOWL
            ############################################################################
            put = re.search(
                "^Put ?([a-zA-Z ]+) into (?:the )?(?:([1-9]\d*)(?:st|nd|rd|th) )?mixing bowl",
                instruction,
            )
            if put is not None:
                mixing_bowl_number = self.prepare_mixing_bowls(put)

                self.check_ingredient_is_valid(put.group(1))

                # Searh for the ingredient value in the list of ingredients
                for ingredient in self.ingr:
                    if ingredient["ingredient_name"] == put.group(1):
                        # put the ingredient in the mixing bowl that corresponds to the number
                        self.put(ingredient, mixing_bowl_number)

            ############################################################################
            # FOLD INGREDIENT INTO MIXING BOWL
            ############################################################################
            fold = re.search(
                "Fold ([a-zA-Z ]+) into (?:the )?(?:(1st|2nd|3rd|[0-9]+th) )?mixing bowl",
                instruction,
            )
            if fold is not None:
                mixing_bowl_number = self.prepare_mixing_bowls(fold)

                self.check_ingredient_is_valid(fold.group(1))

                # Searh for the ingredient value in the list of ingredients
                for ingredient in self.ingr:
                    if ingredient["ingredient_name"] == fold.group(1):
                        # fold the ingredient in the mixing bowl that corresponds to the number
                        self.fold(ingredient, mixing_bowl_number)

            ############################################################################
            # ADD INGREDIENT INTO MIXING BOWL
            ############################################################################
            add = re.search(
                "Add ([a-zA-Z ]+?) to (?:the )?(?:(1st|2nd|3rd|[0-9]+th) )?mixing bowl",
                instruction,
            )
            if add is not None:
                mixing_bowl_number = self.prepare_mixing_bowls(add)

                self.check_ingredient_is_valid(add.group(1))

                # Searh for the ingredient value in the list of ingredients
                for ingredient in self.ingr:
                    if ingredient["ingredient_name"] == add.group(1):
                        # add the ingredient in the mixing bowl that corresponds to the number
                        self.add(ingredient, mixing_bowl_number)

            ############################################################################
            # REMOVE INGREDIENT FROM MIXING BOWL
            ############################################################################
            remove = re.search(
                "Remove ([a-zA-Z ]+?) from (?:the )?(?:(1st|2nd|3rd|[0-9]+th) )?mixing bowl",
                instruction,
            )
            if remove is not None:
                mixing_bowl_number = self.prepare_mixing_bowls(remove)

                self.check_ingredient_is_valid(remove.group(1))

                # Searh for the ingredient value in the list of ingredients
                for ingredient in self.ingr:
                    if ingredient["ingredient_name"] == remove.group(1):
                        # remove the ingredient in the mixing bowl that corresponds to the number
                        self.remove(ingredient, mixing_bowl_number)

            ############################################################################
            # COMBINE INGREDIENT IN MIXING BOWL
            ############################################################################
            combine = re.search(
                "Combine ([a-zA-Z ]+?) into (?:the )?(?:(1st|2nd|3rd|[0-9]+th) )?mixing bowl",
                instruction,
            )
            if combine is not None:
                mixing_bowl_number = self.prepare_mixing_bowls(combine)

                self.check_ingredient_is_valid(combine.group(1))

                # Searh for the ingredient value in the list of ingredients
                for ingredient in self.ingr:
                    if ingredient["ingredient_name"] == combine.group(1):
                        # combine the ingredient in the mixing bowl that corresponds to the number
                        self.combine(ingredient, mixing_bowl_number)

            ############################################################################
            # STIR INGREDIENT IN MIXING BOWL
            ############################################################################
            stir = re.search(
                "Stir ([a-zA-Z ]+?) into (?:the )?(?:(1st|2nd|3rd|[0-9]+th) )?mixing bowl",
                instruction,
            )
            if stir is not None:
                mixing_bowl_number = self.prepare_mixing_bowls(stir)

                self.check_ingredient_is_valid(stir.group(1))

                # Searh for the ingredient value in the list of ingredients
                for ingredient in self.ingr:
                    if ingredient["ingredient_name"] == stir.group(1):
                        # stir the ingredient in the mixing bowl that corresponds to the number
                        self.stir(mixing_bowl_number, ingredient["initial_value"])

            ############################################################################
            # DIVIDE INGREDIENT IN MIXING BOWL
            ############################################################################
            divide = re.search(
                "Divide ([a-zA-Z ]+?) to (?:the )?(?:(1st|2nd|3rd|[0-9]+th) )?mixing bowl",
                instruction,
            )
            if divide is not None:
                mixing_bowl_number = self.prepare_mixing_bowls(divide)

                self.check_ingredient_is_valid(divide.group(1))

                # Searh for the ingredient value in the list of ingredients
                for ingredient in self.ingr:
                    if ingredient["ingredient_name"] == divide.group(1):
                        # divide the ingredient in the mixing bowl that corresponds to the number
                        self.divide(ingredient, mixing_bowl_number)

            ############################################################################
            # LIQUEFY INGREDIENT IN MIXING BOWL
            ############################################################################
            liquefy = re.search(
                "Liquefy contents of the (1st|2nd|3rd|[0-9]+th)? ?mixing bowl",
                instruction,
            )
            if liquefy is not None:
                pass

            ############################################################################
            # LIQUIFY INGREDIENT IN MIXING BOWL
            ############################################################################
            liquify = re.search(
                "Liquify contents of the (1st|2nd|3rd|[0-9]+th)? ?mixing bowl",
                instruction,
            )
            if liquify is not None:
                mixing_bowl_number = self.prepare_mixing_bowls(liquify)
                self.liquefy_all_ingredients(mixing_bowl_number)

            ############################################################################
            # CLEAN MIXING BOWL
            ############################################################################
            clean = re.search(
                "Clean the (1st|2nd|3rd|[0-9]+th)? ?mixing bowl", instruction
            )
            if clean is not None:
                mixing_bowl_number = self.prepare_mixing_bowls(clean)
                self.clean(mixing_bowl_number)

            ############################################################################
            # MIX INGREDIENT IN MIXING BOWL
            ############################################################################
            mix = re.search(
                "Mix the (1st|2nd|3rd|[0-9]+th)? ?mixing bowl well", instruction
            )
            if mix is not None:
                mixing_bowl_number = self.prepare_mixing_bowls(mix)
                self.mix(mixing_bowl_number)

            ############################################################################
            # TAKE INGREDIENT FROM FRIDGE
            ############################################################################
            fridge = re.search("Take ([a-zA-Z]+) from refrigerator", instruction)
            if fridge is not None:
                pass

            ############################################################################
            # POUR INGREDIENT FROM MIXING BOWL
            ############################################################################
            pour = re.search(
                "Pour contents of the (?:the )?(?:([1-9]\d*)(?:st|nd|rd|th) )?mixing bowl into the (?:the )?(?:([1-9]\d*)(?:st|nd|rd|th) )?baking dish",
                instruction,
            )
            if pour is not None:
                pass

            ############################################################################
            # REFREGERATE INGREDIENT IN MIXING BOWL
            ############################################################################
            refrigerate = re.search("Refrigerate (?:for ([0-9]+))? hours", instruction)
            if refrigerate is not None:
                self.refrigerate()

            ############################################################################
            # ADD DRY INGREDIENT TO MIXING BOWL
            ############################################################################
            adddry = re.search(
                "Add dry ingredients(?: to the (1st|2nd|3rd|[0-9]+th) mixing bowl)?",
                instruction,
            )
            if adddry is not None:
                mixing_bowl_number = self.prepare_mixing_bowls(adddry)
                self.add_dry_ingredients(mixing_bowl_number)

            ############################################################################
            # VERB INGREDIENT IN MIXING BOWL
            ############################################################################
            verb = re.search("([a-zA-Z]+) the ([a-zA-Z ]+) ?(?!until)", instruction)
            if verb is not None:
                pass

        print(len(self.mixing_bowls))
        for mixing_bowl in self.mixing_bowls:
            for ingredient in mixing_bowl.ingredients:
                print(
                    f"Ingredient: {ingredient.name} {ingredient.value} {ingredient.measure} {ingredient.measure_type} {ingredient.ingredient_type}"
                )

    # Add the ingredient to the top of the mixing bowl
    def put(self, ingredient, mixing_bowl_number):
        self.mixing_bowls[mixing_bowl_number - 1].ingredients.append(
            Ingredient(
                ingredient["ingredient_name"],
                ingredient["initial_value"],
                ingredient["measure"],
                ingredient["measure_type"],
                ingredient["ingredient_type"],
            )
        )

    # Remove the top ingredient from the mixing bowl and place the new ingredient on top
    def fold(self, ingredient, mixing_bowl_number):
        if len(self.mixing_bowls[mixing_bowl_number - 1].ingredients) == 0:
            raise ValueError(f"Mixing bowl {mixing_bowl_number} is empty")
        self.mixing_bowls[mixing_bowl_number - 1].ingredients.pop()
        self.mixing_bowls[mixing_bowl_number - 1].ingredients.append(
            Ingredient(
                ingredient["ingredient_name"],
                ingredient["initial_value"],
                ingredient["measure"],
                ingredient["measure_type"],
                ingredient["ingredient_type"],
            )
        )

    # Take value from stdin and overwrite the ingredients value
    def take(self, ingredient):
        pass

    # Add the ingredient value to the value of the ingredient at the top of the mixing bowl
    def add(self, ingredient, mixing_bowl_number):
        if len(self.mixing_bowls[mixing_bowl_number - 1].ingredients) == 0:
            raise ValueError(f"Mixing bowl {mixing_bowl_number} is empty")
        self.mixing_bowls[mixing_bowl_number - 1].ingredients[-1].value += ingredient[
            "initial_value"
        ]

    # Remove the ingredient value from the value of the ingredient at the top of the mixing bowl
    def remove(self, ingredient, mixing_bowl_number):
        if len(self.mixing_bowls[mixing_bowl_number - 1].ingredients) == 0:
            raise ValueError(f"Mixing bowl {mixing_bowl_number} is empty")
        self.mixing_bowls[mixing_bowl_number - 1].ingredients[-1].value -= ingredient[
            "initial_value"
        ]

    # Multiply the ingredient value by the value of the ingredient at the top of the mixing bowl
    def combine(self, ingredient, mixing_bowl_number):
        if len(self.mixing_bowls[mixing_bowl_number - 1].ingredients) == 0:
            raise ValueError(f"Mixing bowl {mixing_bowl_number} is empty")
        self.mixing_bowls[mixing_bowl_number - 1].ingredients[-1].value *= ingredient[
            "initial_value"
        ]

    # Divide the ingredient value by the value of the ingredient at the top of the mixing bowl
    def divide(self, ingredient, mixing_bowl_number):
        if len(self.mixing_bowls[mixing_bowl_number - 1].ingredients) == 0:
            raise ValueError(f"Mixing bowl {mixing_bowl_number} is empty")
        self.mixing_bowls[mixing_bowl_number - 1].ingredients[-1].value /= ingredient[
            "initial_value"
        ]

    # Sum all the values of the dry ingredients and add the sum to the top of the mixing bowl
    # as a new ingredient called "dry ingredients"
    def add_dry_ingredients(self, mixing_bowl_number):
        # sum all the dry ingredients
        sum = 0
        for ingredient in self.ingredients:
            if ingredient["ingredient_type"] == "dry":
                sum += ingredient["initial_value"]

        # add the sum to the top of the mixing bowl
        self.mixing_bowls[mixing_bowl_number - 1].ingredients.append(
            Ingredient(
                "dry ingredients",
                sum,
                "",
                "",
                "dry",
            )
        )

    # turn the ingredient outside the mixing bowl into a liquid
    def liquefy_single_ingredient(self, ingredient):
        # search for the ingredient in the mixing bowl
        for ingr in self.ingredients:
            if ingr["ingredient_name"] == ingredient:
                ingr["ingredient_type"] = "liquid"
                return

    # turn all the ingredients inside the mixing bowl into a liquid
    def liquefy_all_ingredients(self, mixing_bowl_number):
        for ingredient in self.mixing_bowls[mixing_bowl_number - 1].ingredients:
            ingredient.ingredient_type = "liquid"

    # move the top element to n positions down the stack, if n > len(stack) then the element is moved to the bottom
    def stir(self, mixing_bowl_number, n):
        if len(self.mixing_bowls[mixing_bowl_number - 1].ingredients) == 0:
            raise ValueError(f"Mixing bowl {mixing_bowl_number} is empty")
        ingredient = self.mixing_bowls[mixing_bowl_number - 1].ingredients.pop()
        n = n % len(self.mixing_bowls[mixing_bowl_number - 1].ingredients)
        self.mixing_bowls[mixing_bowl_number - 1].ingredients.insert(n, ingredient)

    # randomize the order of the ingredients in the mixing bowl
    def mix(self, mixing_bowl_number):
        random.shuffle(self.mixing_bowls[mixing_bowl_number - 1].ingredients)

    # remove all the ingredients from the mixing bowl
    def clean(self, mixing_bowl_number):
        self.mixing_bowls[mixing_bowl_number - 1].ingredients = []

    # Copy the elements from the mixing bowl to the baking dish, if the baking dish is not empty, the elements are added to the top
    def pour(self, mixing_bowl_number, baking_dish_number):
        if len(self.mixing_bowls[mixing_bowl_number - 1].ingredients) == 0:
            raise ValueError(f"Mixing bowl {mixing_bowl_number} is empty")
        if baking_dish_number > len(self.baking_dishes):
            self.baking_dishes.append(
                BakingDish(f"Baking Dish {baking_dish_number}", [])
            )
        for ingredient in self.mixing_bowls[mixing_bowl_number - 1].ingredients:
            self.baking_dishes[baking_dish_number - 1].ingredients.append(ingredient)

    # For loop
    # it starts with the keyword Verb the, followed by an ingredient, the loop checks the value of the ingredient
    # it the value is not 0, the loop executes the instructions inside the loop, if the value is 0, the loop is skipped
    # the loop ends with the keyword Verb [the ingredient] until verbed, the ingredient could be any, but
    # if the ingredient matches with the ingredient on "Verb the ingredient", the value of this ingredient is decremented by 1
    # Watchout for the instruction Set aside, this instruction is used to break the loop
    def verb_loop(self, ingredient1, ingredient2, instructions):
        pass

    # Refrigerate means to end the execution of the program
    def refrigerate(self):
        print("Refrigerating...")
        sys.exit()

    # Serve the dish (print the recipe)
    def serve(self):
        output = ""
        for i in range(0, self.number_of_baking_dishes):
            self.baking_dishes[i].ingredients.reverse()
            for ingredient in baking_dishes[i].ingredients:
                value = ingredient.value
                type = ingredient.inredient_type
                if type == "liquid":
                    value = chr(int(value))
                output += str(value)
        return output


def main():
    script = sys.argv[1]
    with open(script, "r") as f:
        script = f.read()

    chef = Chef(script)
    chef.parse_script()
    chef.execute_script()


if __name__ == "__main__":
    main()
