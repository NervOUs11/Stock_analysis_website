from server import app
import layout      # registers app.layout
import callbacks   # registers all @app.callback decorators

if __name__ == "__main__":
    app.run(debug=True)
