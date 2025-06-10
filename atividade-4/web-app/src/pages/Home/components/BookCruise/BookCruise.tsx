import { useState } from "react";
import TextField from "../../../../components/TextField";
import * as S from "./BookCruise.styles";
import Button from "../../../../components/Button";

const BookCruise = () => {
  const [numberOfPassengers, setNumberOfPassengers] = useState("");
  const [numberOfCabins, setNumberOfCabins] = useState("");
  return (
    <S.Container>
      <h2 style={{ textAlign: "left" }}>Reserve sua viagem</h2>

      <S.CruiseInfoBox>
        <S.CruiseInfoBoxTitle>Nome do Cruzeiro</S.CruiseInfoBoxTitle>
        <S.CruiseInfoBoxSubtitle>Descrição do Cruzeiro</S.CruiseInfoBoxSubtitle>
        <S.CruiseInfoBoxPrice>R$ 1.000,00</S.CruiseInfoBoxPrice>
      </S.CruiseInfoBox>

      <TextField
        label="Nome completo"
        value={numberOfPassengers}
        placeholder="Texto"
        onChange={(e) => {
          setNumberOfPassengers(e.target.value);
        }}
      />

      <TextField
        label="Quantidade de cabines"
        value={numberOfPassengers}
        placeholder="Texto"
        onChange={(e) => {
          setNumberOfPassengers(e.target.value);
        }}
      />

      <TextField
        label="Quantidade de passageiros"
        value={numberOfPassengers}
        placeholder="Texto"
        onChange={(e) => {
          setNumberOfPassengers(e.target.value);
        }}
      />

      <Button onClick={() => {}} label="Reservar" />
    </S.Container>
  );
};

export default BookCruise;
