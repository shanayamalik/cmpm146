from models.model import Model
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten
from tensorflow.keras.optimizers import RMSprop

class BasicModel(Model):
    def _define_model(self, input_shape, categories_count):
        self.model = Sequential([
            # First Conv Block
            Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=input_shape),
            MaxPooling2D(2, 2),
            
            # Second Conv Block
            Conv2D(48, (3, 3), activation='relu', padding='same'),
            MaxPooling2D(2, 2),
            
            # Third Conv Block
            Conv2D(32, (3, 3), activation='relu', padding='same'),
            MaxPooling2D(2, 2),
            
            # Flatten and Dense layers
            Flatten(),
            Dense(64, activation='relu'),
            Dense(categories_count, activation='softmax')
        ])
    
    def _compile_model(self):
        self.model.compile(
            optimizer=RMSprop(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
