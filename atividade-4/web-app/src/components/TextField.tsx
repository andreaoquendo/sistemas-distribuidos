import styled from "styled-components";

const TextFieldContainer = styled.input`
  width: 100%;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
  transition: border-color 0.2s;
`;

interface TextFieldProps {
  value: string;
  placeholder?: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const TextField = ({ value, placeholder, onChange }: TextFieldProps) => {
  return (
    <TextFieldContainer
      value={value}
      onChange={onChange}
      type="text"
      placeholder={placeholder}
    />
  );
};

export default TextField;
