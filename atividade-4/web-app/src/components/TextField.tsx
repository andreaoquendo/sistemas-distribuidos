import styled from "styled-components";
import GlobalStyle from "../constants/GlobalStyle.styles";

const TextFieldLabel = styled.span`
  color: #020817;
  text-align: left;
`;

const TextFieldContainer = styled.input`
  width: 100%;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
  transition: border-color 0.2s;
`;

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-text: left;
  width: 100%;
  justify-content: center;
  gap: 8px;
`;

interface TextFieldProps {
  label?: string;
  value: string;
  placeholder?: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const TextField = ({ label, value, placeholder, onChange }: TextFieldProps) => {
  return (
    <>
      <GlobalStyle />
      <Container>
        <TextFieldLabel>{label}</TextFieldLabel>
        <TextFieldContainer
          value={value}
          onChange={onChange}
          type="text"
          placeholder={placeholder}
        />
      </Container>
    </>
  );
};

export default TextField;
