import { useState } from "react";
import TextField from "../../../../components/TextField";
import * as S from "./BookCruise.styles";

const BookCruise = () => {
  const [numberOfPassengers, setNumberOfPassengers] = useState("");
  const [numberOfCabins, setNumberOfCabins] = useState("");
  return (
    <S.Container>
      <h1>Reserve sua viagem</h1>
      <TextField
        value={numberOfPassengers}
        placeholder="Texto"
        onChange={(e) => {
          setNumberOfPassengers(e.target.value);
        }}
      />
    </S.Container>
  );
};

export default BookCruise;
