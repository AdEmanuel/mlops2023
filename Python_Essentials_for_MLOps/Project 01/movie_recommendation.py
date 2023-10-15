"""
Este script realiza recomendações de filmes com base em um título fornecido
pelo usuário. Ele baixa um conjunto de dados de filmes, carrega os dados
necessários em DataFrames do Pandas, e utiliza técnicas de processamento de texto
e similaridade de cosseno para encontrar filmes semelhantes ao título fornecido.

"""
import os
import re
import logging
import zipfile
import argparse
import requests
import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configuração do logging
logging.basicConfig(level=logging.INFO)

def download_dataset() -> None:
    """
    Realiza o download e extração de um conjunto de dados.

    Returns:
      None
    """
    # URL do arquivo zip
    url="http://files.grouplens.org/datasets/movielens/ml-25m.zip"

    # Nome do arquivo zip a ser baixado
    zip_filename = "ml-25m.zip"

    # Nome da pasta a ser extraída
    extracted_folder = "ml-25m"

    if os.path.exists(extracted_folder):
        logging.info("Os arquivos necessários já existem")
        return

    try:

        logging.info("Iniciando Download...")

        with requests.Session() as session:
            response = session.get(url, stream=True)
            response.raise_for_status()

        with open(zip_filename, 'wb') as zip_file, tqdm(
            desc="Progresso do Download: ",
            total=int(response.headers.get('content-length', 0)),
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for data in response.iter_content(chunk_size=1024):
                zip_file.write(data)
                pbar.update(len(data))

        logging.info("Arquivo %s baixado com sucesso.", zip_filename)
        logging.info("Extraindo arquivos ...")

        with zipfile.ZipFile(zip_filename, 'r') as zip_file:
            file_list = zip_file.namelist()
            with tqdm(
                desc="Progresso da Extração: ",
                total=len(file_list),
                unit="files",) as pbar:
                for file_name in file_list:
                    zip_file.extract(file_name,".")
                    pbar.update(1)

        # Exclui o arquivo .zip após a extração correta
        os.remove(zip_filename)
        logging.info("Arquivo %s removido com sucesso.", zip_filename)

    except requests.exceptions.ConnectionError:
        logging.error("Erro de conexão ao baixar o arquivo")
    except requests.exceptions.RequestException as request_error:
        logging.error("Erro de requisição ao baixar o arquivo: %s", request_error)
    except zipfile.BadZipFile as zip_error:
        logging.error("Erro ao extrair o arquivo %s", zip_error)
    except ValueError as error:
        logging.error("Ocorreu um erro inesperado: %s", str(error))

def load_csv(filepath: str) -> pd.DataFrame:
    """
    Carrega um arquivo CSV em um DataFrame.

    Args:
        filepath (str): Caminho para o arquivo CSV a ser carregado.

    Returns:
        pd.DataFrame: Um DataFrame contendo os dados do arquivo CSV.
    """
    try:
        # Carrega o arquivo CSV em um DataFrame
        data_frame = pd.read_csv(filepath)
        return data_frame
    except pd.errors.ParserError as parser_error:
        print("Ocorreu um erro ao carregar o arquivo CSV: %s", str(parser_error))
        return None

def clean_movie_title(movie_title_input: str) -> str:
    """
    Remove os caracteres especiais presentes nos nome do filme

    Args:
      movie_title_input (str): Título do filme que será "limpado"

    Return:
      str: Título do filme sem caracters especiais
    """

    cleaned_movie_title = re.sub("[^a-zA-Z0-9 ]", "", movie_title_input)
    return cleaned_movie_title

def search_movie_by_title_similarity(query_title: str) -> pd.DataFrame:
    """
    Realiza uma pesquisa de similaridade com base no título fornecido

    Args:
      query_title (str): Título do filme a qual se deseja encontrar similiares

    Returns:
      pd.DataFrame: Dataframe que contém os 5 títulos mais similires ao consultado

    """
    cleaned_query_title = clean_movie_title(query_title)
    query_vector = tfidf_vectorizer.transform([cleaned_query_title])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_movie_indices = np.argpartition(cosine_similarities, -5)[-5:]
    top_movie_results = movies_df.iloc[top_movie_indices].iloc[::-1]

    return top_movie_results

def find_similar_movies(reference_movie_id: int) -> pd.DataFrame:
    """
    Encontra filmes semelhantes com base em um filme de referência.

    Args:
      movie_id (int): ID do filme que se deseja encontrar filmes semelhantes

    Returns:
      pd.DataFrame: DataFrame contendo os filmes mais semelhantes ao filme de referência
    """

    similar_users = ratings_df[
        (ratings_df["movieId"] == reference_movie_id) &
        (ratings_df["rating"] > 4)
    ]["userId"].unique()
    similar_user_recs = ratings_df[
        (ratings_df["userId"].isin(similar_users)) &
        (ratings_df["rating"] > 4
    )]["movieId"]
    similar_user_recs = similar_user_recs.value_counts() / len(similar_users)

    similar_user_recs = similar_user_recs[similar_user_recs > .10]
    all_users = ratings_df[
        (ratings_df["movieId"].isin(similar_user_recs.index)) & (ratings_df["rating"] > 4)]
    all_user_recs = all_users["movieId"].value_counts() / len(all_users["userId"].unique())
    rec_percentages = pd.concat([similar_user_recs, all_user_recs], axis=1)
    rec_percentages.columns = ["similar", "all"]

    rec_percentages["score"] = rec_percentages["similar"] / rec_percentages["all"]
    rec_percentages = rec_percentages.sort_values("score", ascending=False)

    return (
        rec_percentages.head(10).merge(movies_df, left_index=True, right_on="movieId")
        [["score", "title", "genres"]]
    )

if __name__ == '__main__':

    #Tratamento para receber o título do filme através da linha de comando
    parser = argparse.ArgumentParser(description='Recomendador de Filmes')
    parser.add_argument(
        '-movie_title', type=str, help='Título do filme para pesquisa de similaridade'
    )
    args = parser.parse_args()
    movie_title = args.movie_title

    # Download dos datasets
    download_dataset()

    # Carrega os datasets necessários
    movies_df = load_csv("./ml-25m/movies.csv")
    ratings_df = load_csv("./ml-25m/ratings.csv")

    # Adicionando ao dataset nova coluna com títulos de filmes sem caracteres especiais
    movies_df["clean_title"] = movies_df["title"].apply(clean_movie_title)

    # Cria uma instância do TfidfVectorizer para calcular o TF-IDF
    tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    # Calcula o TF-IDF para os títulos de filmes limpos
    tfidf_matrix = tfidf_vectorizer.fit_transform(movies_df["clean_title"])

    # Use a função de pesquisa para encontrar o filme correspondente
    results = search_movie_by_title_similarity(movie_title)

    if not results.empty:
        # Obtém o ID do filme correspondente
        movie_id = results.iloc[0]["movieId"]

        # Função find_similar_movies encontra os 10 filmes mais similares
        similar_movies = find_similar_movies(movie_id)

        # Exibe os resultados da busca
        if similar_movies.empty:
            print(f"Não há sugestões de similaridade para o filme {movie_title}")
        else:
            print(f"Os 10 filmes mais similares a {movie_title} são:", )
            print(similar_movies)
