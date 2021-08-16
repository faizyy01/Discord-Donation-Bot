FROM gorialis/discord.py
WORKDIR /app
COPY . .
CMD ["python", "Run.py"]