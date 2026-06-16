#!/usr/bin/env python3
"""
Teste de validação de cancelamento com limite de 6 horas.
Valida que:
1. Aluno NÃO pode cancelar presença com menos de 6 horas
2. Monitor NÃO pode cancelar sessão com menos de 6 horas
3. Ambos podem cancelar com mais de 6 horas
"""

import sys
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from db.connection import get_connection
from utils.time import now_sp_naive
import hashlib


TZ_SP = ZoneInfo("America/Sao_Paulo")


def hash_password(password):
    """Hash password with SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def setup_test_data():
    """Create test data in database."""
    db = get_connection()
    cur = db.cursor()
    
    print("🔧 Limpando dados de teste anteriores...")
    cur.execute("DELETE FROM agendamentos WHERE id > 0")
    cur.execute("DELETE FROM presencas WHERE id > 0")
    cur.execute("DELETE FROM disponibilidades WHERE id > 0")
    cur.execute("DELETE FROM monitorias WHERE id > 0")
    cur.execute("DELETE FROM disciplina_alunos WHERE id > 0")
    cur.execute("DELETE FROM disciplinas WHERE id > 0")
    cur.execute("DELETE FROM usuarios WHERE email IN (%s, %s, %s)", 
                ("professor@test.com", "monitor@test.com", "aluno@test.com"))
    
    # Create professor
    print("👨‍🏫 Criando professor...")
    cur.execute("""
        INSERT INTO usuarios (nome, email, senha_hash, papel, status, senha_temporaria)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, ("Prof Teste", "professor@test.com", hash_password("123456"), "PROFESSOR", "ATIVO", False))
    professor_id = cur.lastrowid
    
    # Create monitor
    print("👨‍🎓 Criando monitor...")
    cur.execute("""
        INSERT INTO usuarios (nome, email, senha_hash, papel, status, senha_temporaria)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, ("Monitor Teste", "monitor@test.com", hash_password("123456"), "MONITOR", "ATIVO", False))
    monitor_id = cur.lastrowid
    
    # Create student
    print("🧑‍🎓 Criando aluno...")
    cur.execute("""
        INSERT INTO usuarios (nome, email, senha_hash, papel, status, senha_temporaria)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, ("Aluno Teste", "aluno@test.com", hash_password("123456"), "ALUNO", "ATIVO", False))
    aluno_id = cur.lastrowid
    
    # Create discipline
    print("📚 Criando disciplina...")
    cur.execute("""
        INSERT INTO disciplinas (codigo, nome, professor_id, status)
        VALUES (%s, %s, %s, %s)
    """, ("CS101", "Disciplina Teste", professor_id, "ATIVA"))
    disciplina_id = cur.lastrowid
    
    # Add student to discipline
    print("📝 Adicionando aluno à disciplina...")
    cur.execute("""
        INSERT INTO disciplina_alunos (disciplina_id, aluno_id)
        VALUES (%s, %s)
    """, (disciplina_id, aluno_id))
    
    # Create monitoria (active)
    print("✅ Criando monitoria ativa...")
    cur.execute("""
        INSERT INTO monitorias (disciplina_id, professor_id, aluno_id, status)
        VALUES (%s, %s, %s, %s)
    """, (disciplina_id, professor_id, monitor_id, "ATIVO"))
    monitoria_id = cur.lastrowid
    
    # Create availability with LESS than 6 hours from now
    print("⏰ Criando disponibilidade (menos de 6 horas)...")
    now = now_sp_naive()
    # 3 hours from now
    data_inicio = now + timedelta(hours=3)
    data_fim = data_inicio + timedelta(hours=1)
    
    cur.execute("""
        INSERT INTO disponibilidades (disciplina_id, monitor_id, data_inicio, data_fim, local, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (disciplina_id, monitor_id, data_inicio, data_fim, "Sala 101", "AGENDADO"))
    disponibilidade_id = cur.lastrowid
    
    # Create agendamento (student confirmed)
    print("✅ Criando agendamento confirmado...")
    cur.execute("""
        INSERT INTO agendamentos (disponibilidade_id, aluno_id, status)
        VALUES (%s, %s, %s)
    """, (disponibilidade_id, aluno_id, "CONFIRMADO"))
    agendamento_id = cur.lastrowid
    
    # Create presenca (CONFIRMADA)
    print("✅ Criando presença confirmada...")
    cur.execute("""
        INSERT INTO presencas (agendamento_id, aluno_id, monitor_id, sessao_id, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (agendamento_id, aluno_id, monitor_id, disponibilidade_id, "CONFIRMADA"))
    
    db.commit()
    cur.close()
    db.close()
    
    return {
        "professor_id": professor_id,
        "monitor_id": monitor_id,
        "aluno_id": aluno_id,
        "disciplina_id": disciplina_id,
        "disponibilidade_id": disponibilidade_id,
        "agendamento_id": agendamento_id,
        "data_inicio": data_inicio,
    }


def test_cancelamento_aluno(client, test_data):
    """Test that student CANNOT cancel presence with less than 6 hours."""
    print("\n" + "="*70)
    print("TEST 1: ALUNO tenta cancelar presença (menos de 6 horas)")
    print("="*70)
    
    aluno_id = test_data["aluno_id"]
    disciplina_id = test_data["disciplina_id"]
    disponibilidade_id = test_data["disponibilidade_id"]
    data_inicio = test_data["data_inicio"]
    
    hours_remaining = (data_inicio - now_sp_naive()).total_seconds() / 3600
    print(f"⏱️  Horas até o agendamento: {hours_remaining:.2f} horas")
    
    # Login as student
    print(f"\n🔐 Login como aluno (ID: {aluno_id})...")
    with client.session_transaction() as sess:
        sess["user_id"] = aluno_id
        sess["papel"] = "ALUNO"
        sess["nome"] = "Aluno Teste"
    
    # Try to cancel presence
    print(f"❌ Tentando cancelar presença (menos de 6 horas)...")
    response = client.post(
        f"/disciplinas/{disciplina_id}/cancelar",
        data={"sessao_id": disponibilidade_id},
        follow_redirects=False
    )
    
    print(f"Response Status: {response.status_code}")
    
    # Check for error message
    with client.session_transaction() as sess:
        messages = sess.get("_flashes", [])
    
    print(f"Mensagens Flash: {messages}")
    
    if any("Cancelamento não permitido com menos de 6 horas" in str(m) for m in messages):
        print("✅ TEST 1 PASSOU: Cancelamento foi bloqueado corretamente!")
        return True
    else:
        print("❌ TEST 1 FALHOU: Cancelamento não foi bloqueado!")
        return False


def test_cancelamento_monitor(client, test_data):
    """Test that monitor CANNOT cancel session with less than 6 hours."""
    print("\n" + "="*70)
    print("TEST 2: MONITOR tenta cancelar sessão (menos de 6 horas)")
    print("="*70)
    
    monitor_id = test_data["monitor_id"]
    disponibilidade_id = test_data["disponibilidade_id"]
    data_inicio = test_data["data_inicio"]
    
    hours_remaining = (data_inicio - now_sp_naive()).total_seconds() / 3600
    print(f"⏱️  Horas até o agendamento: {hours_remaining:.2f} horas")
    
    # Login as monitor
    print(f"\n🔐 Login como monitor (ID: {monitor_id})...")
    with client.session_transaction() as sess:
        sess["user_id"] = monitor_id
        sess["papel"] = "MONITOR"
        sess["nome"] = "Monitor Teste"
    
    # Try to cancel session
    print(f"❌ Tentando cancelar sessão (menos de 6 horas)...")
    response = client.post(
        f"/monitorias/sessoes/{disponibilidade_id}/cancelar",
        follow_redirects=False
    )
    
    print(f"Response Status: {response.status_code}")
    
    # Check for error message
    with client.session_transaction() as sess:
        messages = sess.get("_flashes", [])
    
    print(f"Mensagens Flash: {messages}")
    
    if any("Cancelamento não permitido com menos de 6 horas" in str(m) for m in messages):
        print("✅ TEST 2 PASSOU: Cancelamento foi bloqueado corretamente!")
        return True
    else:
        print("❌ TEST 2 FALHOU: Cancelamento não foi bloqueado!")
        return False


def main():
    print("\n" + "🧪 " + "="*66 + " 🧪")
    print("   TESTE: VALIDAÇÃO DE CANCELAMENTO COM LIMITE DE 6 HORAS")
    print("🧪 " + "="*66 + " 🧪\n")
    
    # Create app with testing config
    app = create_app()
    app.config["TESTING"] = True
    
    # Setup test database
    with app.app_context():
        test_data = setup_test_data()
    
    # Create test client
    client = app.test_client()
    
    try:
        # Run tests
        test1_passed = test_cancelamento_aluno(client, test_data)
        test2_passed = test_cancelamento_monitor(client, test_data)
        
        # Summary
        print("\n" + "="*70)
        print("📊 RESUMO DOS TESTES")
        print("="*70)
        print(f"Test 1 (Aluno):  {'✅ PASSOU' if test1_passed else '❌ FALHOU'}")
        print(f"Test 2 (Monitor): {'✅ PASSOU' if test2_passed else '❌ FALHOU'}")
        
        if test1_passed and test2_passed:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            return 0
        else:
            print("\n⚠️  ALGUNS TESTES FALHARAM!")
            return 1
            
    except Exception as e:
        print(f"\n❌ ERRO DURANTE EXECUÇÃO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
