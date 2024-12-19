from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# Conectar ao MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Substitua pela sua URI, se necessário

# Seleciona o banco de dados
db = client["sac_centro_informatica"]

# Seleciona a coleção
colecao_status = db["status_problemas"]

# Lista de status
status_list = ["pendente", "em_andamento", "finalizado"]

# Inicializar os documentos de status se não existirem
for status in status_list:
    if colecao_status.count_documents({"status": status}) == 0:
        colecao_status.insert_one({
            "status": status,
            "problemas": []
        })

def criar_problema(numero_usuario, mensagem, classificacao):
    problema = {
        "problema_id": ObjectId(),
        "numero_usuario": numero_usuario,
        "mensagem": mensagem,
        "classificacao": classificacao,
        "data_criacao": datetime.utcnow()
    }
    resultado = colecao_status.update_one(
        {"status": "pendente"},
        {"$push": {"problemas": problema}}
    )
    return problema["problema_id"]

def obter_problemas_por_status(status):
    documento = colecao_status.find_one({"status": status})
    if documento:
        return documento["problemas"]
    return []

def atualizar_status_problema(problema_id, novo_status):
    # Encontrar e remover o problema do status atual
    problema = None
    for status in status_list:
        documento = colecao_status.find_one({"status": status, "problemas.problema_id": problema_id})
        if documento:
            problema = next((p for p in documento["problemas"] if p["problema_id"] == problema_id), None)
            colecao_status.update_one(
                {"status": status},
                {"$pull": {"problemas": {"problema_id": problema_id}}}
            )
            break

    if problema:
        # Atualizar o status
        problema["status"] = novo_status
        # Remover o campo 'status' do problema, pois a posição no documento já indica o status
        problema.pop("status", None)
        # Adicionar ao novo status
        colecao_status.update_one(
            {"status": novo_status},
            {"$push": {"problemas": problema}}
        )
        return True
    return False

def finalizar_problema(problema_id):
    # Atualizar o status para 'finalizado'
    return atualizar_status_problema(problema_id, "finalizado")

# Exemplos de uso

if __name__ == "__main__":
    # Criar um novo problema
    novo_id = criar_problema(
        numero_usuario="123456",
        mensagem="Não consigo acessar a internet.",
        classificacao="Conectividade"
    )
    print(f"Problema criado com ID: {novo_id}")

    # Listar problemas pendentes
    print("\nProblemas Pendentes:")
    pendentes = obter_problemas_por_status("pendente")
    for problema in pendentes:
        print(problema)

    # Atualizar o status para 'em_andamento'
    atualizado = atualizar_status_problema(novo_id, "em_andamento")
    if atualizado:
        print("\nStatus atualizado para 'em_andamento'.")
    else:
        print("\nFalha ao atualizar o status.")

    # Listar problemas em andamento
    print("\nProblemas em Andamento:")
    em_andamento = obter_problemas_por_status("em_andamento")
    for problema in em_andamento:
        print(problema)

    # Finalizar o problema
    finalizado = finalizar_problema(novo_id)
    if finalizado:
        print("\nProblema finalizado com sucesso.")
    else:
        print("\nFalha ao finalizar o problema.")

    # Listar problemas finalizados
    print("\nProblemas Finalizados:")
    finalizados = obter_problemas_por_status("finalizado")
    for problema in finalizados:
        print(problema)
