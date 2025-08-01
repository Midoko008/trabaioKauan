import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Carrinho() {
  const [produtos, setProdutos] = useState([]);
  const [valorTotal, setValorTotal] = useState('0.00');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:5000/pedido')
      .then(res => res.json())
      .then(data => {
        setProdutos(data.pratos || []);
        setValorTotal(data.valor_total || '0.00');
        setLoading(false);
      })
      .catch(() => {
        alert('Erro ao carregar carrinho');
        setLoading(false);
      });
  }, []);

  function remover_do_carrinho(e, pratoId) {
    e.stopPropagation();

    fetch(`http://localhost:5000/pedido/${pratoId}`, {
      method: 'DELETE'
    })
      .then(res => res.json())
      .then(data => {
        alert(data.mensagem || data.erro);

        if (data.mensagem) {
          const novaLista = [...produtos];
          const index = novaLista.findIndex(p => p.id === pratoId);
          if (index !== -1) {
            novaLista.splice(index, 1);
            setProdutos(novaLista);

            const novoTotal = novaLista.reduce((total, p) => total + p.preco, 0);
            setValorTotal(novoTotal.toFixed(2));
          }
        }
      })
      .catch(() => alert('Erro ao remover dos pedidos'));
  }

  function formatarPeso(peso) {
    if (peso >= 1000) {
      return `${(peso / 1000).toFixed(2)} kg`;
    }
    return `${peso} g`;
  }

  if (loading) return <div>Carregando pedidos...</div>;

  return (
    <div className="pagina-inicial">
      <button className="botao-perfil" onClick={() => navigate('/paginaInicial')}>
        Voltar
      </button>
      <h1>Seus Pedidos</h1>

      <div className="lista-produtos">
        {produtos.length === 0 && <p>Você não pediu nada ainda</p>}

        {produtos.map((produto) => (
          <div key={produto.id} className="card-produto">
            <img src={produto.imagem_url} alt={produto.nome} className="imagem-produto" />
            <h3>{produto.nome}</h3>
            <p>Preço: R$ {produto.preco.toFixed(2)}</p>
            <p>Peso: {formatarPeso(produto.peso)}</p>

            <button
              className="botao-carrinho remover"
              onClick={(e) => remover_do_carrinho(e, produto.id)}
              aria-label={`Remover ${produto.nome} do carrinho`}
              title="Remover do carrinho"
            >
              <svg
                className="icone-carrinho"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                width="20"
                height="20"
              >
                <circle cx="9" cy="21" r="1"></circle>
                <circle cx="20" cy="21" r="1"></circle>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
              </svg>
            </button>
          </div>
        ))}
      </div>

      <div className="carrinho-footer">
        <span className="precoTotal">Total: R$ {valorTotal}</span>
        <button className="confirmarCompra">Confirmar compra</button>
      </div>
    </div>
  );
}
