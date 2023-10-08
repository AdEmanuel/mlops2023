import pytest
import pandas as pd
from movie_recommendation import clean_movie_title, search_movie_by_title_similarity, find_similar_movies

# Vamos criar alguns dados de teste para usar nos testes
# Você pode substituir isso pelos dados reais, se preferir
movies_df = pd.DataFrame({'title': ['Movie A', 'Movie B', 'Movie C'],
                          'clean_title': ['MovieA', 'MovieB', 'MovieC']})

# Teste para a função clean_movie_title
def test_clean_movie_title():
    assert clean_movie_title('Movie A!') == 'MovieA'
    assert clean_movie_title('Movie B@') == 'MovieB'
    assert clean_movie_title('Movie C#') == 'MovieC'