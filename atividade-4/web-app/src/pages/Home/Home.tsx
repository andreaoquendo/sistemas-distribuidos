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
  const [mensagens, setMensagens] = useState<string[]>([]);
  const [notification, setNotification] = useState<boolean>(false);

  const [reservaId, setReservaId] = useState<string>("");

  const [userId, setUserId] = useState<string>("");
  const [reservaStreams, setReservaStreams] = useState<
    Record<string, EventSource>
  >({});

  const [data, setData] = useState({
    destino: "",
    data_embarque: "",
    porto_embarque: "",
  });

  const handleNotification = () => {
    if (!userId) return;
    if (notification == true) return;
    console.log("Ativando notificações para o usuário:", userId);

    const eventSource = new EventSource(
      `http://localhost:5002/promocoes?user_id=${userId}`
    );
    setNotification(true);

    eventSource.onmessage = (event) => {
      setMensagens((prev) => [...prev, event.data]);
      alert(event.data);
    };

    eventSource.onerror = (err) => {
      console.error("Erro na conexão SSE:", err);
      alert("Usuário não encontrado ou conexão falhou.");
      setNotification(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
      setNotification(false);
    };
  };

  const handleReservaUpdates = (reservaId: string) => {
    if (!reservaId) return;
    if (reservaStreams[reservaId]) return; // já está escutando essa reserva

    console.log("Conectando ao stream de status da reserva:", reservaId);

    const eventSource = new EventSource(
      `http://localhost:5002/status-reserva?reserva_id=${reservaId}`
    );

    // Atualiza estado com nova conexão ativa
    setReservaStreams((prev) => ({ ...prev, [reservaId]: eventSource }));

    eventSource.onmessage = (event) => {
      console.log(`Atualização para reserva ${reservaId}:`, event.data);
      setMensagens((prev) => [
        ...prev,
        `📦 [Reserva ${reservaId}] ${event.data}`,
      ]);
      alert(`📦 [Reserva ${reservaId}] ${event.data}`);
    };

    eventSource.onerror = (err) => {
      console.error(`Erro na conexão SSE da reserva ${reservaId}:`, err);
      alert(`Erro com a reserva ${reservaId}. Conexão encerrada.`);
      eventSource.close();

      // Remove do estado
      setReservaStreams((prev) => {
        const atualizado = { ...prev };
        delete atualizado[reservaId];
        return atualizado;
      });
    };
  };

  const cancelarPromocao = async (userId: string) => {
    try {
      const response = await axios.delete(
        `http://localhost:5002/cancelar-promocao/${userId}`
      );
      console.log("Promoção cancelada:", response.data);
      return response.data;
    } catch (error) {
      console.error("Erro ao cancelar promoção:", error);
      // throw error;
    }
  };

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

  const cancelReserva = async (reservaId: string) => {
    try {
      const response = await axios.delete(
        `http://127.0.0.1:5002/cancelar-reserva/${reservaId}`
      );
      console.log("Reserva cancelada:", response.data);
      return response.data;
    } catch (error) {
      console.error("Erro ao cancelar reserva:", error);
      throw error;
    }
  };

  const activatePromocao = async (userId: string) => {
    try {
      const response = await axios.post("http://localhost:5002/promocoes", {
        user_id: userId,
      });
      console.log("Promoção ativada:", response.data);
      return response.data;
    } catch (error) {
      console.error("Erro ao ativar promoção:", error);
      throw error;
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
          <S.Section>
            <h1>Discover Your Perfect Cruise</h1>
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
          </S.Section>

          <S.Section
            style={{
              backgroundColor: "#fff",
              borderRadius: "16px",
              padding: "24px",
            }}
          >
            <h1>Cancele sua reserva!</h1>
            <div style={{ display: "flex", alignItems: "end", gap: "8px" }}>
              <TextField
                name="reserva_id"
                label="ID da Reserva"
                value={reservaId}
                onChange={(e) => {
                  setReservaId(e.target.value);
                }}
              />
              <Button
                label="Cancelar reserva"
                onClick={() => {
                  cancelReserva(reservaId);
                }}
              />
            </div>
          </S.Section>
          <S.Section style={{ marginTop: "24px" }}>
            <h1>Gerencie suas promoções!</h1>

            <div style={{ display: "flex", gap: "12px" }}>
              <TextField
                label="Código de usuário"
                name="user_id"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                placeholder="Silvana"
              />
              <Button label="Ativar" onClick={() => handleNotification()} />
              <Button
                label="Inscrever"
                onClick={() => activatePromocao(userId)}
              />
              <Button
                label="Cancelar"
                onClick={() => cancelarPromocao(userId)}
              />
            </div>
          </S.Section>
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
            onSubmit={(reservaId?: string) => {
              setOpenModal(false);
              if (reservaId) {
                setReservaId(reservaId);
                handleReservaUpdates(reservaId);
              }
            }}
          />
        </Modal>
      )}
    </>
  );
};

export default Home;
