import { useState } from "react";
import styled from "styled-components";

const Page = styled.div`
  padding: 2rem;
`;

const Consulta = () => {
  const [destinoBahamas, setDestinoBahamas] = useState(false);
  const [destinoAlaska, setDestinoAlaska] = useState(false);
  const [destinoRoma, setDestinoRoma] = useState(false);

  const [portoFort, setPortoFort] = useState(false);
  const [portoVancouver, setPortoVancouver] = useState(false);
  const [portoBarcelona, setPortoBarcelona] = useState(false);

  return (
    <Page>
      <h1>Consulta de Cruzeiros</h1>
      <p>Aqui você pode consultar cruzeiros disponíveis.</p>
      <h3>Qual destino?</h3>
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
      <h3>Que data?</h3>
      <input
        type="date"
        style={{ marginTop: "1rem", padding: "0.5rem", fontSize: "1rem" }}
        onChange={(e) => console.log("Data selecionada:", e.target.value)}
      />
      <h3></h3>
      <h3>Porto de Embarque?</h3>
      <label>
        <input
          type="checkbox"
          checked={portoFort}
          onChange={(e) => setPortoFort(e.target.checked)}
          style={{ marginRight: "0.5rem" }}
        />
        Fort Lauderdale
      </label>
      <br />
      <label>
        <input
          type="checkbox"
          checked={portoVancouver}
          onChange={(e) => setPortoVancouver(e.target.checked)}
          style={{ marginRight: "0.5rem" }}
        />
        Vancouver
      </label>
      <br />
      <label>
        <input
          type="checkbox"
          checked={portoBarcelona}
          onChange={(e) => setPortoBarcelona(e.target.checked)}
          style={{ marginRight: "0.5rem" }}
        />
        Barcelona
      </label>
      <button
        onClick={() => {
          console.log("oi");
        }}
      >
        Procurar
      </button>
    </Page>
  );
};

export default Consulta;
