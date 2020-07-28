FROM python:3
WORKDIR /usr/src/ranom_gen_app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["./start_app.sh"]
