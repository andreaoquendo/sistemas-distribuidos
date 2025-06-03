import styled from "styled-components";

export const CardBox = styled.div`
  display: flex;
  flex-direction: column;
  align-items: left;
  justify-content: center;
  width: 100%;
  transition: box-shadow 0.2s;

  padding: 18px;
  gap: 4px;
  border-radius: 16px;
  background-color: #fff;
  border: 1px solid #e0e0e0;

  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }

  h3 {
    margin-bottom: 8px;
  }

  line-height: 22px;
`;

export const Button = styled.button`
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

export const PriceSpan = styled.span`
  font-size: 24px;
  font-weight: 600;
  color: #007bff;
  text-align: right;
  margin-bottom: 8px;
`;

export const DatesBox = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  color: #3f3f3f;
  font-size: 14px;
`;
