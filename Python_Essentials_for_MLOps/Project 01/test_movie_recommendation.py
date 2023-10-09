import pandas as pd
from movie_recommendation import clean_movie_title

def test_clean_movie_title():
    
    """
    Testa a função clean_movie_title para garantir que ela remove os caracteres especiais das strings passadas
    """

    assert clean_movie_title('Jumanji (1995)') == 'Jumanji 1995'
    assert clean_movie_title('Twelve Monkeys (a.k.a. 12 Monkeys) (1995)') == 'Twelve Monkeys aka 12 Monkeys 1995'
    assert clean_movie_title('Arsenio Hall: Smart and Classy (2019)') == 'Arsenio Hall Smart and Classy 2019'



