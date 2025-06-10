import styled from "styled-components";

export const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 500px;
  gap: 16px;
`;

export const CruiseInfoBox = styled.div`
  display: flex;
  flex-direction: column;
  align-items: left;
  justify-content: center;
  width: 100%;
  padding: 18px;
  gap: 4px;
  border-radius: 16px;
  background-color: #eff6ff;
`;

export const CruiseInfoBoxTitle = styled.h3`
  font-size: 16px;
`;

export const CruiseInfoBoxSubtitle = styled.h4`
  font-size:14px:
  color: #4b5563;
  font-weight: 400;
`;

export const CruiseInfoBoxPrice = styled.span`
  font-size: 24px;
  font-weight: 600;
  color: #2563eb;
  text-align: left;
  margin-bottom: 8px;
  margin-top: 8px;
  font-weight: 700;
  font-size: 20px;
`;
