import { CustomButton } from "../../../../components/Button";
import type { Cruise } from "../../../../constants/types/Cruise";
import * as S from "./CruiseCard.styles";
import { CalendarTodayOutlined, Crib } from "@mui/icons-material";

interface CruiseCardProps {
  cruise: Cruise;
  onClick: () => void;
}

const CruiseCard = ({ cruise, onClick }: CruiseCardProps) => {
  return (
    <S.CardBox>
      <h3>{cruise.nome_do_cruzeiro}</h3>
      <p style={{ margin: "4px" }}>
        Viagem de {cruise.quantidade_noites}. Passa por{" "}
        {cruise.lugares_visitados} no navio {cruise.nome_navio}.
      </p>
      <S.DatesBox>
        <CalendarTodayOutlined style={{ color: "#3f3f3f", height: "14px" }} />
        Embarque: {cruise.data_embarque}
      </S.DatesBox>

      <S.PriceSpan>R${cruise.valor_pessoa} p/ pessoa</S.PriceSpan>
      <CustomButton onClick={onClick}>Reservar</CustomButton>
    </S.CardBox>
  );
};

export default CruiseCard;
