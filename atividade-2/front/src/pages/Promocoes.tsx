import { useState } from "react";
import styled from "styled-components";

const Page = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  width: 100%;
  padding: 2rem;
  text-align: center;
  gap: 40px;
`;

const SubscriptionBox = styled.div`
  width: 500px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
`;

const Promocoes = () => {
  const [email, setEmail] = useState("");
  const [destinoBahamas, setDestinoBahamas] = useState(false);
  const [destinoAlaska, setDestinoAlaska] = useState(false);
  const [destinoRoma, setDestinoRoma] = useState(false);

  const handleSubscribe = async () => {
    const destinos = [];
    if (destinoBahamas) destinos.push("Bahamas");
    if (destinoAlaska) destinos.push("Alaska");
    if (destinoRoma) destinos.push("Roma");

    const subscriptionData = {
      email,
      destinos,
    };

    try {
      const response = await fetch("http://localhost:8080/subscribe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(subscriptionData),
      });

      if (response.ok) {
        alert("Inscrição realizada com sucesso!");
        setEmail("");
        setDestinoBahamas(false);
        setDestinoAlaska(false);
        setDestinoRoma(false);
      } else {
        alert("Erro ao realizar inscrição. Tente novamente.");
      }
    } catch (error) {
      console.error("Erro ao se inscrever:", error);
      alert("Erro ao realizar inscrição. Tente novamente.");
    }
  };

  return (
    <Page>
      <div>
        <h1>Receba avisos de promoções do seu destino</h1>
        <p>Coloque seu email e escolha os destinos</p>
      </div>
      <SubscriptionBox>
        <input
          type="email"
          placeholder="Seu email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ padding: "0.5rem", width: "100%" }}
        />
        <div
          style={{ textAlign: "left", marginTop: "1rem", marginBottom: "1rem" }}
        >
          <label>
            <input
              type="checkbox"
              checked={destinoBahamas}
              style={{ marginRight: "0.5rem" }}
              onChange={(e) => setDestinoBahamas(e.target.checked)}
            />
            Bahamas
          </label>
          <br />
          <label>
            <input
              type="checkbox"
              checked={destinoAlaska}
              onChange={(e) => setDestinoAlaska(e.target.checked)}
              style={{ marginRight: "0.5rem" }}
            />
            Alaska
          </label>
          <br />
          <label>
            <input
              type="checkbox"
              checked={destinoRoma}
              onChange={(e) => setDestinoRoma(e.target.checked)}
              style={{ marginRight: "0.5rem" }}
            />
            Roma
          </label>
        </div>
        <button
          onClick={() => {
            console.log("Email:", email);
            console.log("Destinos:", {
              Bahamas: destinoBahamas,
              Alaska: destinoAlaska,
              Roma: destinoRoma,
            });

            handleSubscribe();
          }}
          style={{ padding: "0.5rem" }}
        >
          Se inscrever
        </button>
      </SubscriptionBox>
    </Page>
  );
};

export default Promocoes;
