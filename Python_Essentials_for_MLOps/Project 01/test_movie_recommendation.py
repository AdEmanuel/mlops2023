"""
Teste unitário para a função do sistema recomendador de filmes.
"""

from movie_recommendation import clean_movie_title

def test_clean_movie_title():
    """
    Testa a função clean_movie_title para garantir que ela remove os
    caracteres especiais das strings passadas
    """

    assert clean_movie_title('Jumanji (1995)') == 'Jumanji 1995'
    assert clean_movie_title('F.U.B.A.R (2019)') == 'FUBAR 2019'
    assert clean_movie_title('Gumby: The Movie (1995)') == 'Gumby The Movie 1995'
