import * as React from "react";
import GlobalStyle from "../../constants/GlobalStyle.styles";
import * as S from "./Home.styles";
import CruiseCard from "./components/CruiseCard/CruiseCard";
import Modal from "../../components/Modal";
import { useState } from "react";
import { Book, CribOutlined } from "@mui/icons-material";
import BookCruise from "./components/BookCruise/BookCruise";
import axios from "axios";
import { useEffect } from "react";
import type { Cruise } from "../../constants/types/Cruise";
import Button from "../../components/Button";
import TextField from "../../components/TextField";

type CruiseCardProps = {
  title: string;
  description: string;
  price: string;
  onClick: () => void;
};

const Home = () => {
  const [openModal, setOpenModal] = useState(false);
  const [cruises, setCruises] = useState<Cruise[]>([]);
  const [selectedCruise, setSelectedCruise] = useState<Cruise | null>(null);

  const [data, setData] = useState({
    destino: "",
    data_embarque: "",
    porto_embarque: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = () => {
    fetchCruises();
    console.log("Form submitted with data:", data);
  };

  const fetchCruises = async () => {
    try {
      const params: any = {};
      if (data.destino) params.destino = data.destino;
      if (data.data_embarque) params.data_embarque = data.data_embarque;
      if (data.porto_embarque) params.porto_embarque = data.porto_embarque;

      const response = await axios.get("http://localhost:5002/itinerarios", {
        params,
      });
      setCruises(response.data.itinerarios);
      console.log("Cruises fetched successfully", response.data.itinerarios);
    } catch (error) {
      console.error("Failed to fetch cruises", error);
    }
  };

  useEffect(() => {
    fetchCruises();
  }, []);
  return (
    <>
      <GlobalStyle />
      <S.PageContainer>
        <S.HomeContainer>
          <h2>Cruises: {cruises.length}</h2>
          <h1 style={{ marginBottom: "12px" }}>Discover Your Perfect Cruise</h1>
          <span style={{ marginBottom: "24px" }}>
            From tropical paradises to cultural odysseys, find the cruise that
            matches your dreams.
          </span>

          <S.SearchContainer>
            <TextField
              label="Destino"
              name="destino"
              value={data.destino}
              onChange={handleChange}
              placeholder="Digite o destino"
            />

            <TextField
              label="Porto de Embarque"
              name="porto_embarque"
              value={data.porto_embarque}
              onChange={handleChange}
              placeholder="Digite o porto de embarque"
            />

            <TextField
              label="Data de Embarque"
              name="data_embarque"
              value={data.data_embarque}
              onChange={handleChange}
              placeholder="Digite a data de embarque (dd/mm/yyyy)"
            />

            <Button label="Filtrar" onClick={handleSubmit} />
          </S.SearchContainer>

          <S.CardsContainer>
            {cruises.map((cruise) => (
              <CruiseCard
                key={cruise.id}
                cruise={cruise}
                onClick={() => {
                  setSelectedCruise(cruise);
                  setOpenModal(true);
                }}
              />
            ))}
          </S.CardsContainer>
        </S.HomeContainer>
      </S.PageContainer>

      {selectedCruise && (
        <Modal
          isOpen={openModal}
          onClose={() => {
            setOpenModal(false);
          }}
        >
          <BookCruise
            cruise={selectedCruise}
            onSubmit={() => {
              setOpenModal(false);
            }}
          />
        </Modal>
      )}
    </>
  );
};

export default Home;
