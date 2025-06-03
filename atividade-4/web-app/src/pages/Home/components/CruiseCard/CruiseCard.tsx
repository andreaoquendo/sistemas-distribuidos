import { CustomButton } from "../../../../components/Button";
import * as S from "./CruiseCard.styles";
import { CalendarTodayOutlined } from "@mui/icons-material";

interface CruiseCardProps {
  title: string;
  description: string;
  price: string;
  onClick: () => void;
}

const CruiseCard = ({
  title,
  description,
  price,
  onClick,
}: CruiseCardProps) => {
  return (
    <S.CardBox>
      <h3>{title}</h3>
      <p>{description}</p>
      <S.DatesBox>
        <CalendarTodayOutlined style={{ color: "#3f3f3f", height: "14px" }} />
        Jul 14, 2024
      </S.DatesBox>

      <S.PriceSpan>{price}</S.PriceSpan>
      <CustomButton onClick={onClick}>Reservar</CustomButton>
    </S.CardBox>
  );
};

export default CruiseCard;
