#!/usr/bin/env python3
"""Script para testar o login e verificar se o sistema está funcionando."""

import requests
import sys
from rich.console import Console
from rich.table import Table

console = Console()

BASE_URL = "http://localhost:8086/api/v1"

def test_login():
    """Testa o login com credenciais padrão."""
    console.print("\n[bold blue]🔐 Testando Login...[/bold blue]\n")
    
    # Credenciais de teste
    credentials = {
        "email": "admin@test.com",
        "password": "admin123456"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=credentials,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            console.print("[green]✅ Login bem-sucedido![/green]")
            console.print(f"[dim]Token: {data['access_token'][:50]}...[/dim]")
            return data['access_token']
        else:
            console.print(f"[red]❌ Login falhou: {response.status_code}[/red]")
            console.print(f"[dim]{response.text}[/dim]")
            return None
            
    except requests.exceptions.ConnectionError:
        console.print("[red]❌ Erro: Não foi possível conectar ao backend[/red]")
        console.print("[yellow]💡 Certifique-se de que o backend está rodando:[/yellow]")
        console.print("[dim]   ./start_backend.sh[/dim]")
        return None
    except Exception as e:
        console.print(f"[red]❌ Erro inesperado: {e}[/red]")
        return None

def test_permissions(token):
    """Testa o endpoint de permissões."""
    console.print("\n[bold blue]🔑 Testando Permissões...[/bold blue]\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/permissions",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            console.print("[green]✅ Permissões carregadas com sucesso![/green]")
            console.print(f"[dim]Total de permissões: {len(data.get('permissions', []))}[/dim]")
            
            # Mostrar algumas permissões
            perms = data.get('permissions', [])[:10]
            if perms:
                console.print("\n[bold]Primeiras 10 permissões:[/bold]")
                for perm in perms:
                    console.print(f"  • {perm}")
            
            return True
        else:
            console.print(f"[red]❌ Falha ao carregar permissões: {response.status_code}[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Erro: {e}[/red]")
        return False

def test_projects(token):
    """Testa o endpoint de projetos."""
    console.print("\n[bold blue]📁 Testando Projetos...[/bold blue]\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/projects",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            projects = response.json()
            console.print(f"[green]✅ Projetos carregados: {len(projects)} projeto(s)[/green]")
            
            if projects:
                table = Table(title="Projetos")
                table.add_column("Nome", style="cyan")
                table.add_column("Descrição", style="white")
                
                for proj in projects[:5]:  # Mostrar apenas os primeiros 5
                    table.add_row(
                        proj.get('name', 'N/A'),
                        proj.get('description', 'N/A')[:50]
                    )
                
                console.print(table)
            
            return True
        else:
            console.print(f"[red]❌ Falha ao carregar projetos: {response.status_code}[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Erro: {e}[/red]")
        return False

def main():
    """Executa todos os testes."""
    console.print("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]   🧪 Teste de Sistema - BSmart ALM   [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]")
    
    # Teste 1: Login
    token = test_login()
    if not token:
        console.print("\n[red]❌ Testes interrompidos: Login falhou[/red]")
        sys.exit(1)
    
    # Teste 2: Permissões
    perms_ok = test_permissions(token)
    
    # Teste 3: Projetos
    projects_ok = test_projects(token)
    
    # Resumo
    console.print("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]           📊 Resumo dos Testes        [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]\n")
    
    results = [
        ("Login", token is not None),
        ("Permissões", perms_ok),
        ("Projetos", projects_ok),
    ]
    
    table = Table()
    table.add_column("Teste", style="cyan")
    table.add_column("Status", style="white")
    
    all_passed = True
    for test_name, passed in results:
        status = "[green]✅ PASSOU[/green]" if passed else "[red]❌ FALHOU[/red]"
        table.add_row(test_name, status)
        if not passed:
            all_passed = False
    
    console.print(table)
    
    if all_passed:
        console.print("\n[bold green]🎉 Todos os testes passaram![/bold green]")
        console.print("[dim]O sistema está funcionando corretamente.[/dim]\n")
        sys.exit(0)
    else:
        console.print("\n[bold red]⚠️  Alguns testes falharam[/bold red]")
        console.print("[dim]Verifique os logs acima para mais detalhes.[/dim]\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
