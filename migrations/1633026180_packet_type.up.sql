CREATE TABLE packet_type
(
  id smallint NOT NULL,
  name character varying(10) NOT NULL,
  CONSTRAINT "PK_packet_type" PRIMARY KEY (id)
)
WITH (
OIDS=FALSE
);

INSERT INTO packet_type VALUES(1, 'RR_L');
INSERT INTO packet_type VALUES(2, 'COORD');