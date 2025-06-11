import { useState } from "react";
import TextField from "../../../../components/TextField";
import * as S from "./BookCruise.styles";
import Button from "../../../../components/Button";
import type { Cruise } from "../../../../constants/types/Cruise";

type BookCruiseProps = {
  cruise: Cruise;
};

const BookCruise = ({ cruise }: BookCruiseProps) => {
  const [formData, setFormData] = useState({
    fullName: "",
    cabins: "",
    passengers: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const data = new FormData();
    data.append("fullName", formData.fullName);
    data.append("cabins", formData.cabins);
    data.append("passengers", formData.passengers);
    // handle form submission (e.g., send data to API)
  };

  return (
    <S.Container>
      <h2 style={{ textAlign: "left" }}>Reserve sua viagem</h2>

      <S.CruiseInfoBox>
        <S.CruiseInfoBoxTitle>{cruise.nome_do_cruzeiro}</S.CruiseInfoBoxTitle>
        <S.CruiseInfoBoxSubtitle>
          Viagem de {cruise.quantidade_noites}. Passa por{" "}
          {cruise.lugares_visitados} no navio {cruise.nome_navio}. Embarque:{" "}
          {cruise.data_embarque}
        </S.CruiseInfoBoxSubtitle>
        <S.CruiseInfoBoxPrice>
          R$ {cruise.valor_pessoa} por pessoa
        </S.CruiseInfoBoxPrice>
      </S.CruiseInfoBox>

      <TextField
        label="Nome completo"
        value={formData.fullName}
        name="fullName"
        placeholder="Texto"
        onChange={handleChange}
      />

      <TextField
        label="Quantidade de cabines"
        value={formData.cabins}
        name="cabins"
        placeholder="Texto"
        onChange={handleChange}
      />

      <TextField
        label="Quantidade de passageiros"
        name="passengers"
        value={formData.passengers}
        placeholder="Texto"
        onChange={handleChange}
      />

      <Button onClick={() => {}} label="Reservar" />
    </S.Container>
  );
};

export default BookCruise;
