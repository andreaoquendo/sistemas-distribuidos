import styled from "styled-components";

export const PageContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding-top: 36px;
  background-color: #f2f8ff;
`;

export const HomeContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 1500px;
`;

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
`;

export const CardsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 20px;
  width: 100%;
`;

export const PriceSpan = styled.span`
  font-size: 24px;
  font-weight: 600;
  color: #007bff;
  text-align: right;
  margin-bottom: 8px;
`;

export const SearchContainer = styled.div`
  display: flex;
  flex-direction: row;
  gap: 12px;
  align-items: center;
  background-color: #fff;
  padding: 18px;
  border-radius: 16px;
  width: 100%;
`;

export const Section = styled.section`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;

  h1 {
    margin-bottom: 12px;
  }
`;
