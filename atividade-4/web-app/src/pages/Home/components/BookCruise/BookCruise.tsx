import { useState } from "react";
import TextField from "../../../../components/TextField";
import * as S from "./BookCruise.styles";
import Button from "../../../../components/Button";
import type { Cruise } from "../../../../constants/types/Cruise";
import axios from "axios";

type BookCruiseProps = {
  cruise: Cruise;
  onSubmit?: (reservaId?: string) => void;
};

const BookCruise = ({ cruise, onSubmit }: BookCruiseProps) => {
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

  const handleSubmit = () => {
    axios
      .post("http://localhost:5002/reservar", {
        user_id: formData.fullName,
        cruzeiro_id: cruise.id,
        numero_cabines: Number(formData.cabins),
        numero_pessoas: Number(formData.passengers),
      })
      .then((response) => {
        // handle success (e.g., show confirmation)
        alert(`Link de pagamento: ${response.data.link_pagamento}`);
        onSubmit?.(response.data.reserva_id);
      })
      .catch((error) => {
        // handle error (e.g., show error message)
        console.error("Erro ao reservar", error);
        onSubmit?.();
      });
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

      <Button onClick={handleSubmit} label="Reservar" />
    </S.Container>
  );
};

export default BookCruise;
