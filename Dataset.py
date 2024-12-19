from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017/") 

db = client["sac_centro_informatica"]

colecao_status = db["status_problemas"]

status_list = ["pendente", "em_andamento", "finalizado"]

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
        problema["status"] = novo_status

        problema.pop("status", None)
    
        colecao_status.update_one(
            {"status": novo_status},
            {"$push": {"problemas": problema}}
        )
        return True
    return False

def finalizar_problema(problema_id):
    return atualizar_status_problema(problema_id, "finalizado")


if __name__ == "__main__":
    novo_id = criar_problema(
        numero_usuario="123456",
        mensagem="Não consigo acessar a internet.",
        classificacao="Conectividade"
    )
    print(f"Problema criado com ID: {novo_id}")

    print("\nProblemas Pendentes:")
    pendentes = obter_problemas_por_status("pendente")
    for problema in pendentes:
        print(problema)

    atualizado = atualizar_status_problema(novo_id, "em_andamento")
    if atualizado:
        print("\nStatus atualizado para 'em_andamento'.")
    else:
        print("\nFalha ao atualizar o status.")

    print("\nProblemas em Andamento:")
    em_andamento = obter_problemas_por_status("em_andamento")
    for problema in em_andamento:
        print(problema)

    finalizado = finalizar_problema(novo_id)
    if finalizado:
        print("\nProblema finalizado com sucesso.")
    else:
        print("\nFalha ao finalizar o problema.")

    print("\nProblemas Finalizados:")
    finalizados = obter_problemas_por_status("finalizado")
    for problema in finalizados:
        print(problema)
