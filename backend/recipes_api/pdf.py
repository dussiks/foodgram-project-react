import io

from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.response import Response

from .models import CustomUser, RecipeIngredient


def get_shop_ingredients_or_none(user_id: int) -> dict:
    """
    Prepares data about ingredients (name, amount, measurement unit) from
    recipes that are added to shopping_cart of user with given id for
    further transaction to pdf creating.
    :param user_id - id of the user owner of shopping_cart.
    :return: data about all ingredients in shopping_cart.
    """
    try:  # поскольку вызывающая функция ждем либо словарь, либо None, я решил обработать возможное исключение.
        user = CustomUser.objects.get(id=user_id)
    except (models.CustomUser.DoesNotExist, MultipleObjectsReturned):
        return None

    shopping_cart = user.shopping_carts.select_related('recipe').all()
    if not shopping_cart:
        return None

    shop_ingredients = {}
    for item in shopping_cart:
        recipe = item.recipe
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        if not ingredients:
            return None

        for ingredient in ingredients:
            name = ingredient.ingredient.name
            unit = ingredient.ingredient.measurement_unit
            amount = ingredient.amount

            if name not in shop_ingredients:
                shop_ingredients[name] = {
                    'amount': amount,
                    'unit': unit
                }
            else:
                shop_ingredients[name]['amount'] = (
                    shop_ingredients[name]['amount'] + amount
                )
    return shop_ingredients


def create_pdffile_response(user_id: int) -> object:
    """
    Generates pdf format file if user with received id has
    objects in shopping cart.
    :param user_id
    :return: Response object
    """
    pdfmetrics.registerFont(TTFont('Verdana', 'Verdana.ttf'))
    buying_list = get_shop_ingredients_or_none(user_id=user_id)
    if not buying_list:
        error_text = 'No shopping cart or something wrong with other data.'
        return Response(error_text, status=status.HTTP_400_BAD_REQUEST)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
    textobject = pdf.beginText()
    textobject.setTextOrigin(inch, inch)
    textobject.setFont('Verdana', 20)

    pdf_lines = []
    head_line = 'СПИСОК ИНГРЕДИЕНТОВ К ПОКУПКЕ:'
    pdf_lines.append(head_line)
    pdf_lines.append('')
    count = 1
    for item in buying_list:
        amount, unit = buying_list[item]['amount'], buying_list[item]['unit']
        ingredient = f'{count}. {item} - {amount} {unit}'
        pdf_lines.append(ingredient)
        count += 1

    for line in pdf_lines:
        textobject.textLine(line)
    pdf.drawText(textobject)
    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True,
                        filename='buying_list.pdf')
