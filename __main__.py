import connexion

if __name__ == '__main__':

    app = connexion.App(__name__)
    app.add_api('swagger.yaml')
    app.run(port=8080)
