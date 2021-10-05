CREATE TABLE coord (
    id SERIAL PRIMARY KEY,
    marker_id SMALLINT NOT NULL,
    packet_type_id SMALLINT NOT NULL,
    device_sequence_number INT NOT NULL,
    device_tag_id INT NOT NULL,
    x numeric(4,2),
    y numeric(4,2),
    z numeric(4,2),
    error_message VARCHAR(250),
    created_at timestamp NOT NULL
);

ALTER TABLE coord
  ADD CONSTRAINT "FK_coord_marker_id" FOREIGN KEY (marker_id) REFERENCES marker (id)
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE coord
  ADD CONSTRAINT "FK_coord_packet_type_id" FOREIGN KEY (packet_type_id) REFERENCES packet_type (id)
ON UPDATE NO ACTION ON DELETE NO ACTION;