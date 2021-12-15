from newspaper import Article

def article_extractor(urls):

    url = urls
    toi_article = Article(url, language="en")
    toi_article.download()
    toi_article.parse()
    toi_article.nlp()

    """ print("Article's Title:")
    print(toi_article.title)
    print("\n") """

    print("Article's Text:")
    print(toi_article.text)
    print("\n")
    return(toi_article.text)

    """ print("Article's Summary:")
    print(toi_article.summary)
    print("n")

    print("Article's Keywords:")
    print(toi_article.keywords) """
