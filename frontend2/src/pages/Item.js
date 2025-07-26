import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

export default function Item() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [produto, setProduto] = useState(null);
  const [loading, setLoading] = useState(true);
  const [noCarrinho, setNoCarrinho] = useState(false);
  const [usuarioLogado, setUsuarioLogado] = useState(null);

  useEffect(() => {
    // Pega o usuário logado do localStorage (objeto completo)
    const usuario = JSON.parse(localStorage.getItem('cozinheiro'));
    if (!usuario) {
      navigate('/login');
      return;
    }
    setUsuarioLogado(usuario);

    fetch(`http://localhost:5000/pratos/${id}`)
      .then(res => {
        if (!res.ok) throw new Error('Produto não encontrado');
        return res.json();
      })
      .then(data => {
        setProduto(data);
        setLoading(false);
      })
      .catch(err => {
        alert(err.message);
        navigate('/paginaInicial');
      });
  }, [id, navigate]);

  useEffect(() => {
    if (!usuarioLogado) return;

    fetch('http://localhost:5000/pedido', {
      headers: {
        Authorization: `Bearer ${usuarioLogado.id}`
      }
    })
      .then(res => res.json())
      .then(data => {
        const estaNoCarrinho = data.produtos?.some(item => item.id === Number(id)) || false;
        setNoCarrinho(estaNoCarrinho);
      })
      .catch(() => setNoCarrinho(false));
  }, [id, usuarioLogado]);

  if (loading || !produto || !usuarioLogado) return <div>Carregando...</div>;

  // Função para deletar produto
  function deletarProduto() {
    if (!window.confirm('Tem certeza que deseja deletar este produto?')) return;

    fetch(`http://localhost:5000/pratos/${produto.id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${usuarioLogado.id}`
      }
    })
      .then(res => res.json())
      .then(data => {
        alert(data.mensagem || data.erro);
        if (data.mensagem) {
          navigate('/paginaInicial'); // Volta para página inicial após deletar
        }
      })
      .catch(() => alert('Erro ao deletar produto'));
  }

  // Permissão para deletar: se o id do usuário logado é igual ao id do usuário que postou o produto
  const podeDeletar = produto.cozinheiro && usuarioLogado && (produto.cozinheiro.id === usuarioLogado.id);

  return (
    <div className="pagina-inicial" style={{ maxWidth: 600, margin: '40px auto' }}>
      <button className="botao-perfil" onClick={() => navigate('/paginaInicial')}>
        Voltar
      </button>
      <h1>{produto.nome}</h1>
      <img
        src={produto.imagem_url}
        alt={produto.nome}
        style={{ width: '100%', height: 'auto', borderRadius: 8, marginBottom: 20 }}
      />
<p>
  <strong>Preço:</strong> R$ {produto.preco.toFixed(2)}{' '}
  <strong>Peso: {produto.peso >= 1000 ? (produto.peso / 1000).toFixed(2) + ' kg' : produto.peso + ' g'}</strong>
</p>

      {produto.usuario && (
        <p>
          <strong>Postado por: </strong>
          <span
            onClick={() => navigate(`/perfil/${produto.usuario.id}`)}
            style={{ color: '#007bff', cursor: 'pointer', textDecoration: 'underline' }}
          >
            {produto.usuario.nome}
          </span>
        </p>
      )}

      {!noCarrinho && (
        <button
          className="botao-perfil"
          onClick={() => {
            fetch('http://localhost:5000/pedido', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${usuarioLogado.id}`
              },
              body: JSON.stringify({ prato_id: produto.id })
            })
              .then(res => res.json())
              .then(data => {
                alert(data.mensagem || data.erro);
                if (data.mensagem) setNoCarrinho(true);
              })
              .catch(() => alert('Erro ao adicionar ao carrinho'));
          }}
        >
          Adicionar aos pedidos
        </button>
      )}

      {noCarrinho && (
        <button
          className="botao-perfil"
          onClick={() => {
            fetch(`http://localhost:5000/pedido/${produto.id}`, {
              method: 'DELETE',
              headers: {
                Authorization: `Bearer ${usuarioLogado.id}`
              }
            })
              .then(res => res.json())
              .then(data => {
                alert(data.mensagem || data.erro);
                if (data.mensagem) setNoCarrinho(false);
              })
              .catch(() => alert('Erro ao remover do carrinho'));
          }}
          style={{ backgroundColor: '#dc3545' }}
        >
          Remover dos pedidos
        </button>
      )}

      {podeDeletar && (
        <button
          className="botao-perfil"
          style={{ backgroundColor: '#b22222', marginTop: 20 }}
          onClick={deletarProduto}
        >
          Jogar fora
        </button>
      )}
    </div>
  );
}
