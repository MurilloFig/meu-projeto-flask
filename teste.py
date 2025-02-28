import random

def rolar_dados(quantidade, lados):
    if quantidade <= 0 or lados <= 0:
        print("Erro: A quantidade de dados e os lados devem ser maiores que zero.")
        return
    
    resultados = [random.randint(1, lados) for _ in range(quantidade)]
    soma_total = sum(resultados)
    
    print(f"Soma total: {soma_total}")
    
    if quantidade <= 100:
        resultados.sort(reverse=True)
        print(f"Resultados ordenados (decrescente): {resultados}")

if __name__ == "__main__":
    while True:
        quantidade = int(input("Quantos dados deseja lançar? "))
        lados = int(input("Quantos lados cada dado possui? "))
        rolar_dados(quantidade, lados)
        
        continuar = input("Deseja continuar? (s/n): ").strip().lower()
        if continuar != 's':
            break