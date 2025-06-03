import styled, { keyframes } from "styled-components";
import GlobalStyle from "../constants/GlobalStyle.styles";
import { Close } from "@mui/icons-material";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

const fadeIn = keyframes`
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
`;

const scaleIn = keyframes`
  from {
    transform: translate(-50%, -50%) scale(0.9);
    opacity: 0;
  }
  to {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }
`;

const Backdrop = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 100;
  animation: ${fadeIn} 0.3s ease forwards;
`;

const ModalBox = styled.div`
  background-color: #fff;
  padding: 16px;
  position: fixed;
  top: 50%;
  left: 50%;
  border-radius: 8px;
  animation: ${scaleIn} 0.3s ease forwards;
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: flex-end;
`;

const Modal = ({ isOpen, onClose, children }: ModalProps) => {
  if (!isOpen) return null;

  return (
    <>
      <GlobalStyle />
      <Backdrop>
        <ModalBox>
          <ButtonContainer>
            <button
              onClick={onClose}
              style={{ margin: "0", padding: "0", height: "24px" }}
            >
              <Close />
            </button>
          </ButtonContainer>

          {children}
        </ModalBox>
      </Backdrop>
    </>
  );
};

export default Modal;
