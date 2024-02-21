package com.example.timskiproekt.rabbitMQ;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

public class Producer {
    private final static String QUEUE_NAME = "DemoQueue";

    public static void main(String[] argv) throws Exception {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost"); // RabbitMQ server hostname
        factory.setPort(5672); // RabbitMQ server port
        factory.setUsername("guest"); // RabbitMQ username
        factory.setPassword("guest"); // RabbitMQ password

        try (Connection connection = factory.newConnection();
             Channel channel = connection.createChannel()) {
            boolean durable = true; // Make the queue durable
            channel.queueDeclare(QUEUE_NAME, durable, false, false, null);
            String message = "https://www.finki.ukim.mk/";
            channel.basicPublish("", QUEUE_NAME, null, message.getBytes());
            System.out.println("Sent '" + message + "'");
        }
    }
}