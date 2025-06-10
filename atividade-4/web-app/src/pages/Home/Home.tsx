import * as React from "react";
import GlobalStyle from "../../constants/GlobalStyle.styles";
import * as S from "./Home.styles";
import CruiseCard from "./components/CruiseCard/CruiseCard";
import Modal from "../../components/Modal";
import { useState } from "react";
import { Book } from "@mui/icons-material";
import BookCruise from "./components/BookCruise/BookCruise";
const fakeCruiseCards: CruiseCardProps[] = [
  {
    title: "Caribbean Adventure",
    description: "Explore the beautiful Caribbean islands on a 7-day cruise.",
    price: "$999",
    onClick: () => alert("Booked Caribbean Adventure!"),
  },
  {
    title: "Mediterranean Escape",
    description: "Sail through the Mediterranean and visit historic cities.",
    price: "$1299",
    onClick: () => alert("Booked Mediterranean Escape!"),
  },
  {
    title: "Alaskan Expedition",
    description: "Experience the wild beauty of Alaska on this unique cruise.",
    price: "$1499",
    onClick: () => alert("Booked Alaskan Expedition!"),
  },
];

const Home = () => {
  const [openModal, setOpenModal] = useState(false);
  return (
    <>
      <GlobalStyle />
      <S.PageContainer>
        <S.HomeContainer>
          <h1 style={{ marginBottom: "12px" }}>Discover Your Perfect Cruise</h1>
          <span style={{ marginBottom: "24px" }}>
            From tropical paradises to cultural odysseys, find the cruise that
            matches your dreams.
          </span>
          <S.CardsContainer>
            {fakeCruiseCards.map((card, index) => (
              <CruiseCard
                key={index}
                title={card.title}
                description={card.description}
                price={card.price}
                onClick={() => {
                  setOpenModal(true);
                }}
              />
            ))}
          </S.CardsContainer>
        </S.HomeContainer>
      </S.PageContainer>
      <Modal
        isOpen={openModal}
        onClose={() => {
          setOpenModal(false);
        }}
      >
        <BookCruise />
      </Modal>
    </>
  );
};

export default Home;
