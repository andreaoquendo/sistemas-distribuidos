import styled from "styled-components";

export const CustomButton = styled.button`
  padding: 10px 16px;
  border-radius: 8px;
  background-color: #007bff;
  color: #fff;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
  width: 100%;
  font-weight: 600;
`;

interface ButtonProps {
  onClick: () => void;
  label: string;
}

const Button = ({ label, onClick }: ButtonProps) => {
  return <CustomButton onClick={onClick}>{label}</CustomButton>;
};
